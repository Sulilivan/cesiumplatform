<template>
  <div id="cesiumContainer" style="width: 100vw; height: 100vh;"></div>
  
  <DashboardLayer 
    :settings="settings"
    :coords="mouseCoords"
    :currentPointCode="selectedPoint?.point_code"
    :currentPointName="selectedPoint?.point_name"
    @update:settings="updateSettings"
    @select-point="flyToPoint"
  />
</template>

<script setup>
import { onMounted, reactive, watch, ref } from 'vue' // 引入 ref
import { useRouter } from 'vue-router' // 引入 useRouter
import * as Cesium from 'cesium'
import { logout } from '@/utils/api' // 引入 logout 方法
import DashboardLayer from './DashboardLayer.vue' // 引入仪表盘

window.CESIUM_BASE_URL = import.meta.env.VITE_CESIUM_BASE_URL

const router = useRouter() // 获取 router 实例

const viewerRef = ref(null)
const selectedPoint = ref(null)
const mouseCoords = ref('经度: --, 纬度: --, 高程: --米')


// 响应式状态管理
const settings = reactive({
  lighting: true,
  shadows: true,
  antiAliasing: true
})

const updateSettings = (newSettings) => {
  Object.assign(settings, newSettings)
}

const flyToPoint = (point) => {
  selectedPoint.value = point
  if (viewerRef.value && point.longitude && point.latitude) {
    // 添加一个实体标记
    viewerRef.value.entities.removeAll()
    viewerRef.value.entities.add({
        position: Cesium.Cartesian3.fromDegrees(point.longitude, point.latitude, (point.height || 0)),
        point: {
            pixelSize: 10,
            color: Cesium.Color.RED,
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 2
        },
        label: {
            text: point.point_name,
            font: '14pt monospace',
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            outlineWidth: 2,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            pixelOffset: new Cesium.Cartesian2(0, -9)
        }
    })

    viewerRef.value.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(
        point.longitude, 
        point.latitude, 
        (point.height || 0) + 200 // 飞到点上方200米
      ),
      orientation: {
        heading: Cesium.Math.toRadians(0.0),
        pitch: Cesium.Math.toRadians(-45.0),
        roll: 0.0
      },
      duration: 2
    })
  }
}


onMounted(async () => {
  const viewer = new Cesium.Viewer('cesiumContainer', {
    animation: false,
    scene3DOnly: true,
    selectionIndicator: false,
    automaticallyTrackDataSourceClocks: false,
    sceneModePicker: false,
    timeline: true,
    geocoder: false,         // 关闭搜索
    homeButton: false,
    navigationHelpButton: false,
    terrain: Cesium.Terrain.fromWorldTerrain({requestVertexNormals: true}), 
    shadows: settings.shadows,// filepath: d:\github\cesiumapartment\frontend\src\components\CesiumViewer.vue
  })

  viewerRef.value = viewer

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
  } catch (error) {
    console.error(`加载本地 3D Tileset 失败: ${error}`);
  }

  // 开启光照、阴影、HDR 和抗锯齿
  viewer.scene.globe.enableLighting = true;
  viewer.terrainShadows = Cesium.ShadowMode.ENABLED;
  viewer.scene.msaaSamples = 16;
  viewer.scene.postProcessStages.fxaa.enabled = true;

  // 开启HDR
  if (viewer.scene.highDynamicRangeSupported) {
    viewer.scene.highDynamicRange = true
  }

  // --- 添加北侧水体（上游大面积水域） ---
  function addWater() {
    // 1. 定义水体材质
    const waterMaterial = new Cesium.Material({
      fabric: {
        type: 'Water',
        uniforms: {
          baseWaterColor: new Cesium.Color(0.0, 0.3, 0.5, 0.6), 
          normalMap: '/modeli/myWaterNormals.jpg',
          // 北侧水域狭长，设置高频率以获得细腻波纹
          frequency: 5000.0,      
          animationSpeed: 0.01,   // 降低数值以减缓波浪动画速度
          amplitude: 5.0,         
          specularIntensity: 0.8  
        }
      }
    });

    // 2. 北侧水体坐标范围 
    const waterKeyPoints = [
      101.580092, 28.285723,
      101.698043, 28.285725,
      101.698043, 28.400000,
      101.580092, 28.400000
    ];

    // 3. 创建几何体
    const waterPolygon = new Cesium.PolygonGeometry({
      polygonHierarchy: new Cesium.PolygonHierarchy(
        Cesium.Cartesian3.fromDegreesArray(waterKeyPoints)
      ),
      height:1688,          // 水面高度 (米)，设在模型下方一点
      extrudedHeight: 950,  // 水体底部高度
      vertexFormat: Cesium.EllipsoidSurfaceAppearance.VERTEX_FORMAT
    });

    // 4. 创建图元实例
    const geometryInstance = new Cesium.GeometryInstance({
      geometry: waterPolygon
    });

    // 5. 添加到场景
    viewer.scene.primitives.add(new Cesium.Primitive({
      geometryInstances: geometryInstance,
      appearance: new Cesium.EllipsoidSurfaceAppearance({
        material: waterMaterial,
        aboveGround: true // 确保在地形之上正确渲染
      }),
      show: true,
      shadows: Cesium.ShadowMode.RECEIVE_ONLY // 仅接收阴影
    }));
  }

  // --- 添加南侧水体（下游小面积水域） ---
  function addSouthWater() {
    const waterMaterial = new Cesium.Material({
      fabric: {
        type: 'Water',
        uniforms: {
          baseWaterColor: new Cesium.Color(0.0, 0.3, 0.5, 0.6), 
          normalMap:'/modeli/myWaterNormals.jpg', 
          // 南侧区域较小，使用标准频率
          frequency: 1000.0,      
          animationSpeed: 0.01,   // 保持与北侧一致的慢速流动
          amplitude: 5.0,        
          specularIntensity: 0.8
        }
      }
    });

    // 修正坐标使其与北侧完全对称
    // 北侧纬度跨度约 0.014277，中心轴为 28.285723
    const waterKeyPoints = [
      101.620092, 28.201446, // 左下
      101.658043, 28.201446, // 右下
      101.658043, 28.285723, // 右上
      101.620092, 28.285723  // 左上
    ];

    const waterPolygon = new Cesium.PolygonGeometry({
      polygonHierarchy: new Cesium.PolygonHierarchy(
        Cesium.Cartesian3.fromDegreesArray(waterKeyPoints)
      ),
      height: 1900,          // 高度保持与北侧一致
      extrudedHeight: 940,  // 水底高度
      vertexFormat: Cesium.EllipsoidSurfaceAppearance.VERTEX_FORMAT
    });

    viewer.scene.primitives.add(new Cesium.Primitive({
      geometryInstances: new Cesium.GeometryInstance({
        geometry: waterPolygon
      }),
      appearance: new Cesium.EllipsoidSurfaceAppearance({
        material: waterMaterial,
        aboveGround: true
      }),
      show: true,
      shadows: Cesium.ShadowMode.RECEIVE_ONLY
    }));
  }

  // 执行添加水体
  addWater();
  addSouthWater(); // 执行新增的南侧水体函数

  // 显示鼠标位置坐标
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
  handler.setInputAction(function (movement) {
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