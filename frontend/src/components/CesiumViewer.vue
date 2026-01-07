<template>
  <div id="cesiumContainer" style="width: 100vw; height: 100vh;"></div>
</template>

<script setup>
import { onMounted } from 'vue'
import * as Cesium from 'cesium'

window.CESIUM_BASE_URL = import.meta.env.VITE_CESIUM_BASE_URL

onMounted(() => {
  const viewer = new Cesium.Viewer('cesiumContainer', {
    animation: true,
    timeline: true,
    homeButton: true,
    navigationHelpButton: false,
  })

  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(101.630833, 28.182778, 1000)
  })
})
</script>