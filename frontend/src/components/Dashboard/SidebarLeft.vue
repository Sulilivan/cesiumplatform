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

      <!-- 分类测点列表 -->
      <div class="point-list-container">
        <div class="list-header">监测项目</div>
        <div class="category-list">
          <div 
            v-for="category in categories" 
            :key="category.name" 
            class="category-item"
            :class="{ active: activeCategory === category.name }"
          >
            <!-- 分类标题 -->
            <div class="category-header" @click="toggleCategory(category.name)">
              <span class="category-title">{{ category.name }}</span>
              <span class="arrow" :class="{ rotated: activeCategory === category.name }">▶</span>
            </div>

            <!-- 分类下的测点列表 -->
             <div class="sub-point-list" v-show="activeCategory === category.name">
                <div v-if="getPointsByCategory(category).length === 0" class="no-data">
                  暂无测点
                </div>
                <div 
                  v-for="point in getPointsByCategory(category)" 
                  :key="point.point_code"
                  class="point-item"
                  :class="{ active: currentPointCode === point.point_code }"
                  @click="handlePointClick(point)"
                >
                  <span class="point-icon">📍</span>
                  <span class="point-name">{{ point.point_name }}</span>
                  <span class="point-status normal">正常</span>
                </div>
             </div>
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
const activeCategory = ref(null) // 当前展开的分类

// 定义5个固定的分类
const categories = [
  { name: '上游水位', type: '水位', keyword: '上游' },
  { name: '下游水位', type: '水位', keyword: '下游' },
  { name: '引张线', type: '引张线' },
  { name: '静力水准', type: '静力水准' },
  { name: '倒垂线', type: '倒垂线' },
]

watch(() => props.settings, (newVal) => {
  localSettings.value = { ...newVal }
}, { deep: true })

const updateSettings = () => {
  emit('update:settings', localSettings.value)
}

// 切换分类展开/折叠
const toggleCategory = (categoryName) => {
  if (activeCategory.value === categoryName) {
    activeCategory.value = null // 折叠
  } else {
    activeCategory.value = categoryName // 展开
  }
}

// 获取特定分类下的点
const getPointsByCategory = (category) => {
  if (!points.value) return []
  return points.value.filter(point => {
    // 匹配设备类型
    if (point.device_type !== category.type) {
      return false
    }
    // 如果有关键字（用于区分上下游水位），则需匹配名称
    if (category.keyword) {
      return point.point_name.includes(category.keyword)
    }
    return true
  })
}

// 处理点击测点：选中或取消选中
const handlePointClick = (point) => {
  if (props.currentPointCode === point.point_code) {
    // 如果已选中，则取消选中
    emit('select-point', null)
  } else {
    // 否则选中
    emit('select-point', point)
  }
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
  flex-shrink: 0;
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
  /* 隐藏滚动条但保留功能 */
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 160, 233, 0.5) transparent;
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
  margin-top: 10px;
  margin-bottom: 10px;
  color: #00e5ff;
  font-size: 14px;
  border-left: 3px solid #00e5ff;
  padding-left: 8px;
}

.category-item {
  margin-bottom: 5px;
}

.category-header {
  padding: 10px;
  background: rgba(0, 160, 233, 0.1);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid transparent;
  transition: all 0.3s;
}

.category-header:hover {
  background: rgba(0, 160, 233, 0.2);
  border-color: rgba(0, 160, 233, 0.3);
}

.category-item.active .category-header {
  background: rgba(0, 160, 233, 0.3);
  border-color: #00a0e9;
}

.category-title {
  font-size: 14px;
}

.arrow {
  font-size: 12px;
  transition: transform 0.3s;
}

.arrow.rotated {
  transform: rotate(90deg);
}

.sub-point-list {
  background: rgba(0, 0, 0, 0.2);
  padding: 5px 0;
}

.no-data {
  padding: 10px;
  text-align: center;
  color: #aaa;
  font-size: 12px;
}

.point-item {
  display: flex;
  align-items: center;
  padding: 8px 15px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.point-item:hover {
  background: rgba(0, 160, 233, 0.1);
}

.point-item.active {
  background: linear-gradient(90deg, rgba(0, 160, 233, 0.3), transparent);
  border-left-color: #00e5ff;
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
