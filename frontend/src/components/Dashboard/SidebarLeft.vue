<template>
  <div class="sidebar-wrapper" :class="{ collapsed: isCollapsed }">
    <!-- 收起/展开按钮 -->
    <div class="toggle-btn" @click="toggleSidebar" title="收起/展开">
      {{ isCollapsed ? '▶' : '◀' }}
    </div>

    <div class="sidebar-left" v-show="!isCollapsed">
      <div class="panel-header">
        <div class="header-decoration-left"></div>
        <div class="title">场景视觉控制</div>
        <div class="header-decoration-right"></div>
      </div>
      
      <!-- 场景控制部分：固定不滚动 -->
      <div class="control-section">
        <div class="control-icons">
          <div 
            class="icon-btn" 
            :class="{ active: localSettings.lighting }"
            @click="toggleSetting('lighting')"
            title="开启光照"
          >
            光照
          </div>
          <div 
            class="icon-btn" 
            :class="{ active: localSettings.shadows }"
            @click="toggleSetting('shadows')"
            title="开启阴影"
          >
            阴影
          </div>
          <div 
            class="icon-btn" 
            :class="{ active: localSettings.antiAliasing }"
            @click="toggleSetting('antiAliasing')"
            title="抗锯齿"
          >
            抗锯齿
          </div>
          <div 
            class="icon-btn" 
            :class="{ active: localSettings.hdr }"
            @click="toggleSetting('hdr')"
            title="HDR 高动态范围"
          >
            HDR
          </div>
           <!-- 恢复视角按钮 -->
          <div 
            class="icon-btn btn-reset" 
            @click="$emit('reset-view')"
            title="恢复默认视角"
          >
            复位
          </div>
        </div>

        <div class="divider"></div>

        <div class="list-header">监测列表</div>
      </div>

      <!-- 测点列表部分：可滚动 -->
      <div class="panel-content">
        <!-- 分类测点列表 -->
        <div class="point-list-container">
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
const activeCategory = ref(null) 
const isCollapsed = ref(false)

// 定义5个固定的分类
const categories = [
  { name: '引张线', type: '引张线' },
  { name: '静力水准', type: '静力水准' },
  { name: '倒垂线', type: '倒垂线' },
  { name: '上游水位', type: '水位', keyword: '上游' },
  { name: '下游水位', type: '水位', keyword: '下游' },
]

watch(() => props.settings, (newVal) => {
  localSettings.value = { ...newVal }
}, { deep: true })

// 监听当前选中的点，自动展开对应分类 - 需求 1
watch(() => props.currentPointCode, (newCode) => {
  if (!newCode) return;
  const point = points.value.find(p => p.point_code === newCode);
  if (point) {
    for (const cat of categories) {
      // 模拟匹配逻辑
      if (point.device_type === cat.type) {
        if (cat.keyword && !point.point_name.includes(cat.keyword)) continue;
        activeCategory.value = cat.name;
        break;
      }
    }
  }
})

const toggleSetting = (key) => {
  localSettings.value[key] = !localSettings.value[key];
  emit('update:settings', localSettings.value)
}

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
}

const updateSettings = () => {
  emit('update:settings', localSettings.value)
}

const toggleCategory = (categoryName) => {
  if (activeCategory.value === categoryName) {
    activeCategory.value = null 
  } else {
    activeCategory.value = categoryName 
  }
}

const getPointsByCategory = (category) => {
  if (!points.value) return []
  return points.value.filter(point => {
    if (point.device_type !== category.type) {
      return false
    }
    if (category.keyword) {
      return point.point_name.includes(category.keyword)
    }
    return true
  })
}

const handlePointClick = (point) => {
  if (props.currentPointCode === point.point_code) {
    emit('select-point', null) // 取消选中
  } else {
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
.sidebar-wrapper {
  position: absolute;
  left: 20px;
  top: 100px;
  bottom: 90px;
  width: 300px;
  transition: width 0.3s, transform 0.3s;
  pointer-events: auto; /* 确保自身可点击 */
  z-index: 10;
}

.sidebar-wrapper.collapsed {
  transform: translateX(-300px);
}

.toggle-btn {
  position: absolute;
  right: -25px; /* 放在侧边栏右侧外面 */
  top: 50%;
  width: 25px;
  height: 50px;
  background: rgba(10, 25, 50, 0.8);
  color: #00e5ff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-top-right-radius: 8px;
  border-bottom-right-radius: 8px;
  font-size: 12px;
  border: 1px solid rgba(0, 160, 233, 0.3);
  border-left: none;
  pointer-events: auto; /* 必须加上，因为父容器 DashboardLayer 是穿透的，但 wrapper 是 auto，为了保险 */
}

.sidebar-left {
  width: 100%;
  height: 100%;
  background: rgba(10, 25, 50, 0.8);
  border: 1px solid rgba(0, 160, 233, 0.3);
  box-shadow: 0 0 35px rgba(0, 160, 233, 0.5);
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
  border-radius: 8px; /* 圆角 - 需求 3 */
}


.panel-header {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: rgba(0, 160, 233, 0.1);
  border-bottom: 1px solid rgba(0, 160, 233, 0.3);
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.title {
  color: #00e5ff;
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 1px;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 15px 15px 15px;
}

/* 控制区域固定不滚动 */
.control-section {
  padding: 15px;
  flex-shrink: 0;
}

/* 控制图标样式 - 需求 4 */
.control-icons {
  display: flex;
  justify-content: space-around;
  margin-bottom: 15px;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%; /* 圆形 */
  background: rgba(255, 255, 255, 0.1); /* 半透明 */
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 13px;
  font-weight: bold;
  transition: all 0.3s;
  color: #fff;
  border: 1px solid transparent;
}

.icon-btn:hover {
  background: rgba(0, 160, 233, 0.4);
}

/* 悬停显示文字 */
.icon-btn:hover::after {
  content: attr(title);
  position: absolute;
  bottom: -25px;
  font-size: 12px;
  color: #00e5ff;
  background: rgba(0,0,0,0.8);
  padding: 2px 5px;
  border-radius: 4px;
  white-space: nowrap;
}

.icon-btn.active {
  background: rgba(0, 160, 233, 0.6);
  border-color: #00e5ff;
  box-shadow: 0 0 10px #00e5ff;
}

.divider {
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(0, 160, 233, 0.5), transparent);
  margin: 15px 0;
}

.list-header {
  color: #fff;
  font-size: 14px;
  margin-bottom: 10px;
  padding-left: 10px;
  border-left: 3px solid #00e5ff;
}

.category-item {
  margin-bottom: 5px;
}

.category-header {
  background: rgba(255, 255, 255, 0.05);
  padding: 10px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background 0.2s;
  border-radius: 4px;
}

.category-header:hover {
  background: rgba(0, 160, 233, 0.15);
}

.category-title {
  color: #ccc;
  font-size: 14px;
}

.arrow {
  color: #666;
  font-size: 12px;
  transition: transform 0.3s;
}

.arrow.rotated {
  transform: rotate(90deg);
}

.sub-point-list {
  background: rgba(0, 0, 0, 0.2);
  margin-top: 2px;
  border-radius: 4px;
}

.point-item {
  padding: 8px 10px 8px 25px;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #aaa;
  transition: all 0.2s;
  border-radius: 4px;
}

.point-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.point-item.active {
  background: rgba(0, 160, 233, 0.3);
  color: #00e5ff;
}

.point-icon {
  margin-right: 8px;
}

.point-status {
  margin-left: auto;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
}

.point-status.normal {
  background: rgba(82, 196, 26, 0.2);
  color: #52c41a;
}

/* 复位按钮黄色样式 - 需求 4 */
.btn-reset {
    color: #ffeb3b !important;
    border-color: rgba(255, 235, 59, 0.3) !important;
    background: rgba(255, 235, 59, 0.1) !important;
    font-weight: bold;
}

.btn-reset:hover {
    background: rgba(255, 235, 59, 0.3) !important;
    box-shadow: 0 0 10px #ffeb3b !important;
    color: #fff !important;
}

/* 隐形滚动条样式 - 需求 5 */
.panel-content::-webkit-scrollbar {
  width: 4px; /* 很细 */
}

.panel-content::-webkit-scrollbar-track {
  background: transparent; 
}

.panel-content::-webkit-scrollbar-thumb {
  background: rgba(0, 160, 233, 0.2); 
  border-radius: 2px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 160, 233, 0.5); 
}
</style>