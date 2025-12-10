<template>
  <div id="cesiumContainer" style="width: 100vw; height: 100vh;"></div>
</template>

<script setup>
import { onMounted } from 'vue'
import * as Cesium from 'cesium'

window.CESIUM_BASE_URL = import.meta.env.VITE_CESIUM_BASE_URL

onMounted(async () => {
  const tdtUrl = 'https://t{s}.tianditu.gov.cn/'
  const token = '4b240459b7aca1f4110de39e7b37b38e' // 替换为你的key
  const subdomains = ['0', '1', '2', '3', '4', '5', '6', '7']

  const viewer = new Cesium.Viewer('cesiumContainer', {
    animation: false,
    timeline: false,
    terrain: Cesium.Terrain.fromWorldTerrain({ requestVertexNormals: true }),
    terrainExaggeration: 1.0,
    homeButton: true,
    navigationHelpButton: false,
  })

  // 叠加国界服务
  const iboMap = new Cesium.UrlTemplateImageryProvider({
    url: tdtUrl + 'DataServer?T=ibo_w&x={x}&y={y}&l={z}&tk=' + token,
    subdomains,
    tilingScheme: new Cesium.WebMercatorTilingScheme(),
    maximumLevel: 10
  })
  viewer.imageryLayers.addImageryProvider(iboMap)
  
//   // 将三维球定位到中国(因为自动飞到模型所以注释掉)
//     viewer.camera.flyTo({
//         destination: Cesium.Cartesian3.fromDegrees(103.84, 31.15, 17850000),
//         orientation: {
//             heading :  Cesium.Math.toRadians(348.4202942851978),
//             pitch : Cesium.Math.toRadians(-89.74026687972041),
//             roll : Cesium.Math.toRadians(0)
//         },
//         complete:function callback() {
//             // 定位完成之后的回调函数
//         }
//     });

  try {
    const tileset = await Cesium.Cesium3DTileset.fromUrl('/model/tileset.json')
    viewer.scene.primitives.add(tileset)
    viewer.zoomTo(tileset)
  } catch (error) {
    console.error('3D Tiles 加载失败:', error)
  }
})
</script>