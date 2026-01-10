<template>
  <div class="dashboard-layer">
    <!-- 顶部标题栏 -->
    <div class="top-header">
      <div class="header-bg">
        <h1 class="header-title">重力坝三维数据中心</h1>
        <div class="header-subtitle">Gravity Dam 3D Data Center</div>
      </div>
      <button @click="logout" class="logout-btn-top">
        退出
      </button>
    </div>

    <SidebarLeft 
      :settings="settings"
      :currentPointCode="currentPointCode"
      @update:settings="updateSettings" 
      @select-point="selectPoint"
    />

    <SidebarRight 
      :pointCode="currentPointCode"
      :pointName="currentPointName"
    />

    <BottomBar :coords="coords" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SidebarLeft from './Dashboard/SidebarLeft.vue'
import SidebarRight from './Dashboard/SidebarRight.vue'
import BottomBar from './Dashboard/BottomBar.vue'
import { useRouter } from 'vue-router'
import * as apiUtils from '@/utils/api.js'

const props = defineProps({
  settings: Object,
  coords: String,
  currentPointCode: String,
  currentPointName: String
})

const emit = defineEmits(['update:settings', 'select-point'])
const router = useRouter()

const updateSettings = (newSettings) => {
  emit('update:settings', newSettings)
}

const selectPoint = (point) => {
  emit('select-point', point)
}

const logout = () => {
  apiUtils.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none; /* 让鼠标事件穿透到 Cesium */
}

/* 子组件需要开启 pointer-events */
.dashboard-layer :deep(.sidebar-left),
.dashboard-layer :deep(.sidebar-right),
.dashboard-layer :deep(.bottom-bar),
.dashboard-layer :deep(.top-header) {
  pointer-events: auto;
}

.top-header {
  height: 80px;
  background: url('/header-bg.png') no-repeat center top; /* 假设有个头部背景图，这里暂时用渐变替代 */
  background: linear-gradient(to bottom, rgba(10, 25, 50, 1) 0%, rgba(10, 25, 50, 0) 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  border-bottom: 1px solid rgba(0, 160, 233, 0.3);
}

.header-bg {
    text-align: center;
}

.header-title {
  color: #00e5ff;
  font-size: 32px;
  margin: 0;
  letter-spacing: 4px;
  text-shadow: 0 0 10px #00a0e9;
  font-weight: bold;
}

.header-subtitle {
  color: rgba(255,255,255,0.6);
  font-size: 12px;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.logout-btn-top {
  position: absolute;
  right: 20px;
  top: 20px;
  background: rgba(0, 160, 233, 0.2);
  border: 1px solid #00a0e9;
  color: #fff;
  padding: 5px 15px;
  cursor: pointer;
  clip-path: polygon(10px 0, 100% 0, 100% 100%, 0 100%, 0 10px);
  transition: all 0.3s;
}

.logout-btn-top:hover {
  background: rgba(0, 160, 233, 0.5);
  box-shadow: 0 0 10px #00a0e9;
}
</style>
