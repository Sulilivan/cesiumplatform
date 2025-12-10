<template>
  <CesiumViewer />
</template>

<script setup>
import CesiumViewer from './components/CesiumViewer.vue'
</script>

<style>
@import "cesium/Build/Cesium/Widgets/widgets.css";

html, body, #app {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow: hidden;
}
</style>
