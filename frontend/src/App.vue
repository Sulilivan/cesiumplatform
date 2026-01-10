<template>
  <router-view />
</template>

<script setup>
// import CesiumViewer from './components/CesiumViewer.vue' // 不再需要直接引入
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
