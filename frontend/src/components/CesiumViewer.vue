<template>
  <div id="cesiumContainer" style="width: 100vw; height: 100vh;"></div>
  <div id="mouse-coords" style="position:fixed;left:10px;bottom:10px;z-index:1000;background:rgba(0,0,0,0.6);color:#fff;padding:4px 10px;border-radius:4px;font-size:14px;pointer-events:none;">
    坐标：--
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import * as Cesium from 'cesium'

window.CESIUM_BASE_URL = import.meta.env.VITE_CESIUM_BASE_URL

onMounted(async () => {
  const viewer = new Cesium.Viewer('cesiumContainer', {
    animation: true,
    timeline: true,
    homeButton: true,
    navigationHelpButton: false,
    terrain: Cesium.Terrain.fromWorldTerrain(), // 启用默认立体地形
    shadows: true,
  })

  // 导入本地模型并定位
  try {
    // 模型入口文件为 public/model/tileset.json
    const tileset = await Cesium.Cesium3DTileset.fromUrl('/model/tileset.json');
    viewer.scene.primitives.add(tileset);
    
    // 1. 定义目标位置的经纬度坐标和高度
    const position = Cesium.Cartesian3.fromDegrees(101.649854, 28.295500, 980.42);
    
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
    viewer.zoomTo(tileset);
  } catch (error) {
    console.error(`加载本地 3D Tileset 失败: ${error}`);
  }

  // 开启光照、阴影、HDR 和抗锯齿
  viewer.scene.globe.enableLighting = true;
  viewer.terrainShadows = Cesium.ShadowMode.ENABLED;
  viewer.scene.msaaSamples = 4;
  viewer.scene.postProcessStages.fxaa.enabled = true;

  // 开启HDR
  if (viewer.scene.highDynamicRangeSupported) {
    viewer.scene.highDynamicRange = true
  }

  // 显示鼠标位置坐标
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
  handler.setInputAction(function (movement) {
    const cartesian = viewer.scene.pickPosition(movement.endPosition)
    let text = '坐标：--'
    if (cartesian) {
      const cartographic = Cesium.Cartographic.fromCartesian(cartesian)
      const lon = Cesium.Math.toDegrees(cartographic.longitude).toFixed(6)
      const lat = Cesium.Math.toDegrees(cartographic.latitude).toFixed(6)
      const height = cartographic.height.toFixed(2)
      text = `坐标：${lon}, ${lat} (高程:${height}m)`
    }
    const coordDiv = document.getElementById('mouse-coords')
    if (coordDiv) coordDiv.textContent = text
  }, Cesium.ScreenSpaceEventType.MOUSE_MOVE)
})
</script>