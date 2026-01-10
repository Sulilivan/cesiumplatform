<template>
  <div class="sidebar-left">
    <div class="panel-header">
      <div class="header-decoration-left"></div>
      <div class="title">场景控制 & 测点列表</div>
      <div class="header-decoration-right"></div>
    </div>
    
    <div class="panel-content">
      <!-- 场景控制部分 -->
      <div class="control-group">
        <label class="control-item">
          <input type="checkbox" v-model="localSettings.lighting" @change="updateSettings">
          <span class="custom-checkbox"></span>
          <span class="label-text">开启光照</span>
        </label>
        <label class="control-item">
          <input type="checkbox" v-model="localSettings.shadows" @change="updateSettings">
          <span class="custom-checkbox"></span>
          <span class="label-text">开启阴影</span>
        </label>
        <label class="control-item">
          <input type="checkbox" v-model="localSettings.antiAliasing" @change="updateSettings">
          <span class="custom-checkbox"></span>
          <span class="label-text">抗锯齿</span>
        </label>
      </div>

      <div class="divider"></div>

      <!-- 测点列表部分 -->
      <div class="point-list-container">
        <div class="list-header">监测点列表</div>
        <div class="point-list">
          <div 
            v-for="point in points" 
            :key="point.point_code"
            class="point-item"
            :class="{ active: currentPointCode === point.point_code }"
            @click="selectPoint(point)"
          >
            <span class="point-icon">📍</span>
            <span class="point-name">{{ point.point_name }}</span>
            <span class="point-status normal">正常</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '@/utils/api'

const props = defineProps({
  settings: Object,
  currentPointCode: String
})

const emit = defineEmits(['update:settings', 'select-point'])

const localSettings = ref({ ...props.settings })
const points = ref([])

watch(() => props.settings, (newVal) => {
  localSettings.value = { ...newVal }
}, { deep: true })

const updateSettings = () => {
  emit('update:settings', localSettings.value)
}

const selectPoint = (point) => {
  emit('select-point', point)
}

const fetchPoints = async () => {
  try {
    const res = await api.get('/points/')
    points.value = res.data
  } catch (error) {
    console.error('Fetch points failed:', error)
  }
}

onMounted(() => {
  fetchPoints()
})
</script>

<style scoped>
.sidebar-left {
  position: absolute;
  left: 20px;
  top: 80px;
  width: 260px;
  bottom: 120px;
  background: rgba(10, 25, 50, 0.7);
  border: 1px solid rgba(0, 160, 233, 0.3);
  backdrop-filter: blur(10px);
  color: #fff;
  display: flex;
  flex-direction: column;
  z-index: 100;
  box-shadow: 0 0 20px rgba(0, 160, 233, 0.2) inset;
}

.panel-header {
  height: 40px;
  background: rgba(0, 160, 233, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border-bottom: 1px solid rgba(0, 160, 233, 0.5);
}

.title {
  font-weight: bold;
  font-size: 16px;
  color: #00e5ff;
  text-shadow: 0 0 5px #00e5ff;
}

.panel-content {
  padding: 15px;
  flex: 1;
  overflow-y: auto;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.control-item input {
  display: none;
}

.custom-checkbox {
  width: 16px;
  height: 16px;
  border: 1px solid #00a0e9;
  margin-right: 10px;
  position: relative;
  background: rgba(0,0,0,0.3);
}

.control-item input:checked + .custom-checkbox {
  background: #00a0e9;
}

.divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 160, 233, 0.5), transparent);
  margin: 15px 0;
}

.point-list-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.list-header {
  margin-bottom: 10px;
  font-size: 14px;
  border-left: 3px solid #00e5ff;
  padding-left: 8px;
}

.point-item {
  padding: 10px;
  background: rgba(0, 160, 233, 0.1);
  margin-bottom: 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.point-item:hover, .point-item.active {
  background: rgba(0, 160, 233, 0.3);
  border-color: #00e5ff;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.3) inset;
}

.point-name {
  flex: 1;
  margin-left: 8px;
  font-size: 14px;
}

.point-status {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 2px;
}

.point-status.normal {
  background: rgba(0, 255, 0, 0.2);
  color: #00ff00;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-thumb {
  background: rgba(0, 160, 233, 0.5);
  border-radius: 3px;
}
</style>
