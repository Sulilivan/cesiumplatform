<template>
  <div class="dashboard-layer">
    <!-- 顶部标题栏 -->
    <div class="top-header">
      <div class="header-bg">
        <h1 class="header-title">重力坝三维数据中心</h1>
        <div class="header-subtitle">Gravity Dam 3D Data Center</div>
      </div>
      
      <div class="top-buttons">
          <button v-if="isAdmin" @click="goToAdmin" class="admin-btn-top">
              管理
          </button>
          <button @click="logout" class="logout-btn-top">
              退出
          </button>
      </div>
    </div>

    <SidebarLeft 
      :settings="settings"
      :currentPointCode="currentPointCode"
      @update:settings="updateSettings" 
      @select-point="selectPoint"
      @reset-view="handleResetView"
    />

    <SidebarRight
      :pointCode="currentPointCode"
      :pointName="currentPointName"
      :selectedTime="selectedTime"
      :chartRange="chartRange"
      :selectedFeature="selectedFeature"
      :hasBoundModel="!!currentPointBindId"
      :isAdmin="isAdmin"
      @bind-model="(code) => emit('bind-model', code)"
      @unbind-model="(code) => emit('unbind-model', code)"
    />

    <BottomBar 
      :coords="coords" 
      v-model="selectedTime"
      v-model:chartRange="chartRange"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import SidebarLeft from './Dashboard/SidebarLeft.vue'
import SidebarRight from './Dashboard/SidebarRight.vue'
import BottomBar from './Dashboard/BottomBar.vue'
import { useRouter } from 'vue-router'
import * as apiUtils from '@/utils/api.js'
import * as Cesium from 'cesium'

const props = defineProps({
  settings: Object,
  coords: String,
  currentPointCode: String,
  currentPointName: String,
  currentPointBindId: String, // 当前测点绑定的模型ID
  selectedFeature: Object // 未绑定构件信息
})

const emit = defineEmits(['update:settings', 'select-point', 'bind-model', 'unbind-model'])
const router = useRouter()
const isAdmin = ref(false)
const selectedTime = ref(new Date()) // 时间轴选中的时间
const chartRange = ref(7) // 图表显示的天数范围

// 时间改变时同步到 Cesium 场景
const onTimeChange = (newTime) => {
    if (window.cesiumViewer && newTime instanceof Date) {
        try {
            const julianDate = Cesium.JulianDate.fromDate(newTime)
            window.cesiumViewer.clock.currentTime = julianDate
            // 可选：如果需要光照根据时间变化，确保场景刷新
            window.cesiumViewer.scene.requestRender()
            
            // 更新上游水位显示（南侧水体）
            if (window.updateSouthWaterByTime) {
                window.updateSouthWaterByTime(newTime)
            } else {
                console.warn('水位更新函数尚未初始化')
            }
        } catch (e) {
            console.error('Failed to sync time to Cesium:', e)
        }
    }
}

// 监听 selectedTime 变化
watch(selectedTime, (newTime) => {
    onTimeChange(newTime)
})

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

const goToAdmin = () => {
    router.push('/admin')
}

const handleResetView = () => {
    if (window.resetView) {
        window.resetView()
    }
}

onMounted(() => {
    const userStr = localStorage.getItem('user')
    if (userStr) {
        try {
            const user = JSON.parse(userStr)
            if (user.role === 'admin') {
                isAdmin.value = true
            }
        } catch (e) {
            console.error('Failed to parse user info', e)
        }
    }
})
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
  background: url('/header-bg.png') no-repeat center top; 
  background: linear-gradient(to bottom, rgba(10, 25, 50, 1) 0%, rgba(10, 25, 50, 0) 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.header-bg {
    text-align: center;
}

.header-title {
  color: #00e5ff;
  font-size: 32px;
  margin: 0;
  letter-spacing: 4px;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0, 229, 255, 0.6), 0 0 20px rgba(0, 160, 233, 0.4); /* 发光效果 */
}

.header-subtitle {
  color: rgba(255,255,255,0.6);
  font-size: 12px;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.top-buttons {
    position: absolute;
    right: 20px;
    top: 20px;
    display: flex;
    gap: 10px;
}

.logout-btn-top, .admin-btn-top {
  background: rgba(0, 160, 233, 0.2);
  border: 1px solid #00a0e9;
  color: #fff;
  padding: 5px 15px;
  cursor: pointer;
  border-radius: 4px; /* 圆角矩形 */
  transition: all 0.3s;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 60px;
}

/* 管理按钮：蓝色半透明 */
.admin-btn-top {
    background: rgba(0, 160, 233, 0.2); 
    border: 1px solid #00a0e9;
    box-shadow: 0 0 5px rgba(0, 160, 233, 0.3);
}

.admin-btn-top:hover {
    background: rgba(0, 160, 233, 0.5);
    box-shadow: 0 0 15px #00a0e9;
}

/* 退出按钮：红色半透明 */
.logout-btn-top {
    background: rgba(255, 77, 79, 0.2);
    border: 1px solid #ff4d4f;
    box-shadow: 0 0 5px rgba(255, 77, 79, 0.3);
}

.logout-btn-top:hover {
    background: rgba(255, 77, 79, 0.5);
    box-shadow: 0 0 15px #ff4d4f;
}
</style>
