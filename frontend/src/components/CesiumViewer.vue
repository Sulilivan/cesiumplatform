<template>
  <div id="cesiumContainer" style="width: 100vw; height: 100vh;"></div>
  
  <div 
    v-if="selectedPoint && infoBoxVisible" 
    class="custom-infobox"
    :style="{ left: infoBoxPosition.x + 'px', top: infoBoxPosition.y + 'px' }"
  >
    <div class="infobox-title">{{ selectedPoint.point_name }}</div>
    <div class="infobox-content">编号: {{ selectedPoint.point_code }}</div>
    <div class="infobox-arrow"></div>
  </div>

  <DashboardLayer 
    :settings="settings"
    :coords="mouseCoords"
    :currentPointCode="selectedPoint?.point_code"
    :currentPointName="selectedPoint?.point_name"
    @update:settings="updateSettings"
    @select-point="handleSidebarSelect"
    @bind-model="handleBindModel"
  />
</template>

<script setup>
import { onMounted, reactive, watch, ref } from 'vue' // 引入 ref
import { useRouter } from 'vue-router' // 引入 useRouter
import * as Cesium from 'cesium'
import api from '@/utils/api' // 完整引入 api
import { logout } from '@/utils/api' // 引入 logout 方法
import DashboardLayer from './DashboardLayer.vue' // 引入仪表盘

window.CESIUM_BASE_URL = import.meta.env.VITE_CESIUM_BASE_URL

const router = useRouter() // 获取 router 实例

const viewerRef = ref(null)
const tilesetRef = ref(null)
const selectedPoint = ref(null)
const mouseCoords = ref('经度: --, 纬度: --, 高程: --米')
const allPoints = ref([])
const infoBoxVisible = ref(false)
const infoBoxPosition = reactive({ x: 0, y: 0 })
const isBindingMode = ref(false)
const bindingPointCode = ref(null)

// 测点编号映射关系 (保留以兼容旧数据或硬编码部分，优先使用数据库绑定)
const POINT_MAPPING = {
  'PL1': 'IP1',
  'IP2': 'IP2',
  'IP3': 'IP3'
}

// 响应式状态管理
const settings = reactive({
  lighting: true,
  shadows: true,
  antiAliasing: true,
  hdr: true
})

const updateSettings = (newSettings) => {
  Object.assign(settings, newSettings)
}

const fetchPoints = async () => {
  try {
    const res = await api.get('/points/')
    allPoints.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const handleBindModel = (pointCode) => {
    isBindingMode.value = true
    bindingPointCode.value = pointCode
    alert('进入绑定模式：请点击场景中的模型构件进行绑定')
}

const handleSidebarSelect = (point) => {
  selectedPoint.value = point
  highlightTileFeature(point)
  
  if (point) {
    // 只有绑定了模型的测点才显示气泡和飞向
    if (point.bind_model_id && viewerRef.value) {
        updateInfoBoxForPoint(point)
        // Calculate offset position: Move to North, Look South
        const offsetLat = 0.0005; 
        const offsetHeight = 30;

        viewerRef.value.camera.flyTo({
            destination: Cesium.Cartesian3.fromDegrees(
                point.longitude, 
                point.latitude + offsetLat,
                (point.height || 0) + offsetHeight
            ),
            orientation: {
                heading: Cesium.Math.toRadians(180),
                pitch: Cesium.Math.toRadians(-20),
                roll: 0.0
            },
            duration: 1.5
        });
    } else {
        // 未绑定的测点：隐藏气泡，重置视角
        infoBoxVisible.value = false
        if (window.resetView) window.resetView()
    }
  } else {
    infoBoxVisible.value = false
  }
}

const highlightTileFeature = (point) => {
  if (!tilesetRef.value) return

  
  // 优先使用数据库中的绑定ID
  let targetModelId = point ? point.bind_model_id : null
  
  // 如果没绑定，尝试使用旧的映射
  if (!targetModelId && point) {
      targetModelId = point.point_code
      for (const [key, val] of Object.entries(POINT_MAPPING)) {
        if (val === point.point_code) {
          targetModelId = key
          break
        }
      }
  }

  // 构建样式条件
  // 注意：如果 targetModelId 是 undefined，则不应高亮
  const conditions = [
      ['true', 'color("white")'] 
  ]
  
  if (targetModelId) {
      conditions.unshift([`\${ElementProxyCommonReference} === '${targetModelId}'`, 'color("red")'])
  }

  tilesetRef.value.style = new Cesium.Cesium3DTileStyle({
    color: {
      conditions: conditions
    }
  })
}

const updateInfoBoxForPoint = (point) => {
    if(viewerRef.value && point.longitude && point.latitude) {
        const position = Cesium.Cartesian3.fromDegrees(point.longitude, point.latitude, point.height || 0)
        // 使用 updated API for newer Cesium versions or fallback
        const scene = viewerRef.value.scene;
        const canvasPosition = Cesium.SceneTransforms.worldToWindowCoordinates(scene, position);
        if (canvasPosition) {
            infoBoxPosition.x = canvasPosition.x
            infoBoxPosition.y = canvasPosition.y - 50 
            infoBoxVisible.value = true
        }
    }
}

const updateInfoBoxPositionOnRender = () => {
    if (!selectedPoint.value || !infoBoxVisible.value || !viewerRef.value) return
    
    const point = selectedPoint.value
    const position = Cesium.Cartesian3.fromDegrees(point.longitude, point.latitude, (point.height || 0))
    // Use updated API
    const scene = viewerRef.value.scene;
    const canvasPosition = Cesium.SceneTransforms.worldToWindowCoordinates(scene, position);
    
    if (canvasPosition) {
        infoBoxPosition.x = canvasPosition.x 
        infoBoxPosition.y = canvasPosition.y - 60
    }
}


onMounted(async () => {
  await fetchPoints()
  const viewer = new Cesium.Viewer('cesiumContainer', {
    animation: false,
    scene3DOnly: true,
    selectionIndicator: true, // 恢复原生 - 需求 8
    infoBox: true, // 恢复原生 - 需求 8
    automaticallyTrackDataSourceClocks: false,
    sceneModePicker: false,
    baseLayerPicker: false, // 去掉右上角地图选择 - 需求 5
    fullscreenButton: false, // 去掉右下角全屏按钮 - 需求 5
    timeline: true,
    geocoder: false,         // 关闭搜索
    homeButton: false,
    navigationHelpButton: false,
    terrain: Cesium.Terrain.fromWorldTerrain({requestVertexNormals: true}), 
    shadows: settings.shadows,// filepath: d:\github\cesiumapartment\frontend\src\components\CesiumViewer.vue
  })

  viewerRef.value = viewer
  viewer.scene.postRender.addEventListener(updateInfoBoxPositionOnRender)

  // 提高阴影质量
  viewer.shadowMap.size = 4096; // 提高阴影分辨率
  viewer.shadowMap.maximumDistance = 5000; // 单位：米，根据场景调整

  // 监听并实时更新 Cesium 设置
  watch(() => settings.lighting, (val) => {
    viewer.scene.globe.enableLighting = val
  }, { immediate: true })

  watch(() => settings.shadows, (val) => {
    viewer.shadows = val
    viewer.terrainShadows = val ? Cesium.ShadowMode.ENABLED : Cesium.ShadowMode.DISABLED
  }, { immediate: true })

  watch(() => settings.antiAliasing, (val) => {
    viewer.scene.msaaSamples = val ? 4 : 1
    viewer.scene.postProcessStages.fxaa.enabled = val
  }, { immediate: true })

  watch(() => settings.hdr, (val) => {
    if (viewer.scene.highDynamicRangeSupported) {
        viewer.scene.highDynamicRange = val;
    }
  }, { immediate: true })

  // 隐藏 Cesium logo
  viewer._cesiumWidget._creditContainer.style.display = 'none'

  // 时间轴样式
  viewer.timeline.makeLabel = DateTimeFormatter
  function DateTimeFormatter(datetime) {
    const julianDT = new Cesium.JulianDate()
    Cesium.JulianDate.addHours(datetime, 8, julianDT) // 东八区
    const date = Cesium.JulianDate.toGregorianDate(julianDT)
    let objDT = date.year + '/' + date.month + '/' + date.day + ' ' + date.hour + ':00'
    return objDT
  }

  const date = Cesium.JulianDate.fromDate(new Date())
  viewer.timeline.zoomTo(
    Cesium.JulianDate.addHours(date, -24, new Cesium.JulianDate()),
    Cesium.JulianDate.addHours(date, 24, new Cesium.JulianDate())
  )

  // 导入本地模型并定位
  try {
    // 模型入口文件为 public/model/tileset.json
    const tileset = await Cesium.Cesium3DTileset.fromUrl('/modeli/tileset.json');
    viewer.scene.primitives.add(tileset);
    tilesetRef.value = tileset
    
    // 1. 定义目标位置的经纬度坐标和高度
    const position = Cesium.Cartesian3.fromDegrees(101.649854, 28.295500, 1050.42);
    
    // 2. 获取该位置的东-北-上 (ENU) 转换矩阵（即平移矩阵）
    const translationMatrix = Cesium.Transforms.eastNorthUpToFixedFrame(position);
    
    // 3. 创建顺时针旋转 90 度的旋转矩阵（绕 Z 轴旋转 90 度）
    const rotationMatrix = Cesium.Matrix4.fromRotationTranslation(
      Cesium.Matrix3.fromRotationZ(Cesium.Math.toRadians(90))
    );

    // 4. 创建缩放矩阵
    const scale = 3; 
    const scaleMatrix = Cesium.Matrix4.fromScale(new Cesium.Cartesian3(scale, scale, scale));

    // 5. 合并矩阵：先缩放，再旋转，最后平移
    let modelMatrix = Cesium.Matrix4.multiply(translationMatrix, rotationMatrix, new Cesium.Matrix4());
    tileset.modelMatrix = Cesium.Matrix4.multiply(modelMatrix, scaleMatrix, new Cesium.Matrix4());

    // 页面打开后直接定位到模型
    // viewer.zoomTo(tileset);

    // 设置自定义视角
    const setDefaultView = () => {
      viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(
          101.656054, // 经度
          28.296000,  // 纬度
          3000        // 高度（米），比原来高，便于俯瞰整体
        ),
        orientation: {
          heading: Cesium.Math.toRadians(225), // 朝向正南，绕Z轴旋转180°
          pitch: Cesium.Math.toRadians(-40),   // 俯视角度，-90为正下，-60为较大俯视
          roll: 0
        }
      });
    }
    setDefaultView() // 初始化调用

    // 暴露给 DashboardLayer 调用
    window.resetView = setDefaultView
  } catch (error) {
    console.error(`加载本地 3D Tileset 失败: ${error}`);
  }

  // 点击事件处理
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
  handler.setInputAction(async function (movement) {
    const pickedObject = viewer.scene.pick(movement.position);
    
    // 调试日志：查看点击到了什么
    console.log('Clicked object:', pickedObject);

    if (Cesium.defined(pickedObject) && pickedObject instanceof Cesium.Cesium3DTileFeature) {
        // 尝试获取多个可能的属性名
        const refId = pickedObject.getProperty('ElementProxyCommonReference');
        const name1 = pickedObject.getProperty('name_1');
        const name = pickedObject.getProperty('name'); // 有些模型是 name
        const elementId = pickedObject.getProperty('elementId'); 
        
        console.log('Picked Feature Properties:', { refId, name1, name, elementId });
        
        const finalFeatureId = refId || name1 || name || elementId

        // --- 绑定模式逻辑 ---
        if (isBindingMode.value && bindingPointCode.value) {
            if (finalFeatureId) {
                // 获取点击位置作为测点的新坐标
                const cartesian = viewer.scene.pickPosition(movement.position);
                let newCoords = {};
                if (Cesium.defined(cartesian)) {
                    const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
                    newCoords = {
                        longitude: Cesium.Math.toDegrees(cartographic.longitude),
                        latitude: Cesium.Math.toDegrees(cartographic.latitude),
                        height: cartographic.height
                    };
                }

                if (confirm(`确定将测点 ${bindingPointCode.value} 绑定到构件 ${finalFeatureId} 吗？`)) {
                    try {
                        const point = allPoints.value.find(p => p.point_code === bindingPointCode.value)
                        
                        // 同时更新 bind_model_id 和 坐标
                        const updatePayload = { 
                            bind_model_id: finalFeatureId 
                        }
                        if (newCoords.longitude) {
                            Object.assign(updatePayload, newCoords)
                        }

                        await api.put(`/points/${bindingPointCode.value}`, updatePayload)
                        
                        // 更新前端数据
                        await fetchPoints()
                        
                        alert('绑定成功！')
                        // 重新选中以刷新高亮
                        const newPoint = allPoints.value.find(p => p.point_code === bindingPointCode.value)
                        handleSidebarSelect(newPoint)
                    } catch (e) {
                        console.error(e)
                        alert('绑定失败: ' + e.message)
                    } finally {
                        isBindingMode.value = false
                        bindingPointCode.value = null
                    }
                }
            } else {
                alert('未识别到有效的构件ID，无法绑定')
            }
            return // 绑定模式下不处理后续点击逻辑
        }
        // ------------------
        
        let targetPointCode = null;

        // 0. 优先尝试通过数据库绑定的 ID 匹配
        if (finalFeatureId) {
             const boundPoint = allPoints.value.find(p => p.bind_model_id === finalFeatureId)
             if (boundPoint) {
                 targetPointCode = boundPoint.point_code
             }
        }

        // 1. 尝试通过 ElementProxyCommonReference 匹配 (兼容旧)
        if (!targetPointCode && refId && POINT_MAPPING[refId]) {
             targetPointCode = POINT_MAPPING[refId];
        } 
        // 2. 如果没有直接匹配，尝试从 name_1 解析 (例如 "IP:IP2:253389" -> "IP2")
        else if (!targetPointCode && name1) {
             const parts = name1.split(':');
             if (parts.length >= 2) {
                 const potentialDetails = parts[1]; // 取中间部分
                 if (POINT_MAPPING[potentialDetails]) {
                     targetPointCode = POINT_MAPPING[potentialDetails];
                 } else if (allPoints.value.find(p => p.point_code === potentialDetails)) {
                     targetPointCode = potentialDetails;
                 }
             }
        }

        console.log('Target Point Code:', targetPointCode);

        if (targetPointCode) {
             const point = allPoints.value.find(p => p.point_code === targetPointCode);
             if (point) {
                 // Toggle logic: If already selected, deselect. - 需求 1
                 if (selectedPoint.value && selectedPoint.value.point_code === targetPointCode) {
                     handleSidebarSelect(null);
                     setDefaultView(); // 1. Deselect returns to default view
                 } else {
                     handleSidebarSelect(point);
                 }
             } else {
                 console.warn('找到代码但未找到测点数据:', targetPointCode);
                 handleSidebarSelect(null); // 清除选中
                 setDefaultView(); // 1. Unknown code returns to default view
             }
        } else {
             console.warn('未能匹配到测点代码');
             // 如果点击了模型但没匹配到，清除选中
             handleSidebarSelect(null); 
             setDefaultView(); // 1. Unbound model click returns to default view
        }

    } else {
        // console.log('未点击到 3D Tile Feature');
        handleSidebarSelect(null);
        setDefaultView(); // 1. Click empty space returns to default view (if desired, but usually good practice to reset state)
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

  // 开启光照、阴影、HDR 和抗锯齿
  viewer.scene.globe.enableLighting = true;
  viewer.terrainShadows = Cesium.ShadowMode.ENABLED;
  viewer.scene.msaaSamples = 4; // 适度降低以提高性能，16可能太高
  viewer.scene.postProcessStages.fxaa.enabled = true;

  // 修复透明透视和穿模问题
  // 强制开启深度检测，防止模型被错误遮挡或透视 (Fix "clipping/transparency" error)
  viewer.scene.globe.depthTestAgainstTerrain = true; 
  // 开启对数深度缓冲区，减少 z-fighting
  viewer.scene.logarithmicDepthBuffer = true;
  // 注意：orderIndependentTranslucency 在新版 Cesium 中是只读属性，不能设置

  // 开启HDR
  if (viewer.scene.highDynamicRangeSupported) {
    viewer.scene.highDynamicRange = true
  }

  // --- 添加北侧水体（上游大面积水域） ---
  function addWater() {
    const waterPrimitive = new Cesium.Primitive({
      geometryInstances: new Cesium.GeometryInstance({
        geometry: new Cesium.PolygonGeometry({
          polygonHierarchy: new Cesium.PolygonHierarchy(
            Cesium.Cartesian3.fromDegreesArray([
              101.580092, 28.285723,
              101.698043, 28.285725,
              101.698043, 28.400000,
              101.580092, 28.400000
            ])
          ),
          height: 1688
        })
      }),
      appearance: new Cesium.EllipsoidSurfaceAppearance({
        material: new Cesium.Material({
          fabric: {
            type: 'Water',
            uniforms: {
              baseWaterColor: new Cesium.Color(0.2, 0.5, 0.4, 0.6),
              normalMap: '/modeli/myWaterNormals.jpg',
              frequency: 1000.0,
              animationSpeed: 0.01,
              amplitude: 10.0,
              specularIntensity: 0.8
            }
          }
        })
      })
    });
    viewer.scene.primitives.add(waterPrimitive);
    console.log('上游水体已添加 (Primitive + Water Material)');
  }

  // --- 添加南侧水体（下游小面积水域） ---
  function addSouthWater() {
    const waterPrimitive = new Cesium.Primitive({
      geometryInstances: new Cesium.GeometryInstance({
        geometry: new Cesium.PolygonGeometry({
          polygonHierarchy: new Cesium.PolygonHierarchy(
            Cesium.Cartesian3.fromDegreesArray([
              101.620092, 28.201446,
              101.658043, 28.201446,
              101.658043, 28.285723,
              101.620092, 28.285723
            ])
          ),
          height: 1900
        })
      }),
      appearance: new Cesium.EllipsoidSurfaceAppearance({
        material: new Cesium.Material({
          fabric: {
            type: 'Water',
            uniforms: {
              baseWaterColor: new Cesium.Color(0.2, 0.5, 0.4, 0.6),
              normalMap: '/modeli/myWaterNormals.jpg',
              frequency: 1000.0,
              animationSpeed: 0.01,
              amplitude: 10.0,
              specularIntensity: 0.8
            }
          }
        })
      })
    });
    viewer.scene.primitives.add(waterPrimitive);
    console.log('下游水体已添加 (Primitive + Water Material)');
  }

  // 执行添加水体
  addWater();
  addSouthWater(); // 执行新增的南侧水体函数

  // 显示鼠标位置坐标
  const moveHandler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
  moveHandler.setInputAction(function (movement) {
    const cartesian = viewer.scene.pickPosition(movement.endPosition)
    if (cartesian) {
      const cartographic = Cesium.Cartographic.fromCartesian(cartesian)
      const lon = Cesium.Math.toDegrees(cartographic.longitude).toFixed(6)
      const lat = Cesium.Math.toDegrees(cartographic.latitude).toFixed(6)
      const height = cartographic.height.toFixed(2)
      mouseCoords.value = `经度: ${lon}, 纬度: ${lat}, 高程: ${height}米`
    } else {
      mouseCoords.value = '经度: --, 纬度: --, 高程: --米'
    }

  }, Cesium.ScreenSpaceEventType.MOUSE_MOVE)
})
</script>

<style scoped>
/* 整个容器 */
#cesiumContainer {
  overflow: hidden;
  position: relative;
}

.custom-infobox {
  position: absolute;
  background: rgba(10, 25, 50, 0.85);
  border: 1px solid #00a0e9;
  padding: 10px 15px;
  border-radius: 4px;
  color: #fff;
  transform: translate(-50%, -100%);
  pointer-events: none;
  z-index: 1000;
  box-shadow: 0 0 15px rgba(0, 160, 233, 0.4);
  backdrop-filter: blur(4px);
  min-width: 120px;
  text-align: center;
}

.infobox-title {
  font-size: 16px;
  font-weight: bold;
  color: #00e5ff;
  margin-bottom: 5px;
}

.infobox-content {
  font-size: 12px;
  color: #ccc;
}

.infobox-arrow {
  position: absolute;
  bottom: -6px;
  left: 50%;
  margin-left: -6px;
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid #00a0e9;
}


/* 调整 Cesium InfoBox (弹窗) 位置，防止被右侧栏遮挡 */
:deep(.cesium-infoBox) {
  top: 90px !important;       /* 避开顶部标题栏 */
  right: 360px !important;    /* 避开右侧面板 (320px + 20px padding + buffer) */
  max-width: 400px;
}

/* 上移时间轴，防止被底部栏遮挡 */
:deep(.cesium-viewer-timelineContainer) {
  bottom: 40px !important;    /* 底部栏高度 */
  left: 0 !important;
  right: 0 !important;
}

/* 同时也调整底部其他控件的位置（如果有的话） */
:deep(.cesium-viewer-bottom) {
  bottom: 40px !important;
}
</style>