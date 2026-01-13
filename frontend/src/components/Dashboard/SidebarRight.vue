<template>
  <div class="sidebar-wrapper" :class="{ collapsed: !pointCode }">
    <div class="sidebar-right">
      <div class="panel-header">
        <div class="title">{{ pointName || '测点详情' }}</div>
        <button v-if="pointCode" class="bind-btn" @click="$emit('bind-model', pointCode)" title="绑定3D模型">
          🔗
        </button>
      </div>
      
      <div class="panel-content">
        <div v-if="pointCode">
          <!-- 当前时间的监测值（根据时间轴） -->
          <div class="section-title">
            <span class="title-icon">📍</span>
            选中时间监测值
          </div>
          <div class="current-value-card">
            <div class="value-main">
              <span class="value-number">{{ formatValue(currentTimeValue) }}</span>
              <span class="value-unit">{{ unit }}</span>
            </div>
            <div class="value-label">{{ isWaterLevel ? '水位' : '位移' }}</div>
            <div class="value-time">{{ formatDate(selectedTime) }}</div>
            <div v-if="currentTimeValue !== null && latestData.value !== undefined" class="value-diff" :class="valueDiffClass">
              {{ valueDiffText }}
            </div>
          </div>

          <div class="divider"></div>

          <!-- 实时数据表格 -->
          <div class="section-title">
            <span class="title-icon">📊</span>
            最新监测数据
          </div>
          <table class="data-table">
              <thead>
                  <tr>
                      <th>指标</th>
                      <th>数值</th>
                  </tr>
              </thead>
              <tbody>
                  <tr>
                      <td>{{ isWaterLevel ? '最新水位' : '最新位移' }}</td>
                      <td class="value">{{ formatValue(latestData.value) }} <span class="unit">{{ unit }}</span></td>
                  </tr>
                  <tr>
                      <td>监测时间</td>
                      <td>{{ formatDate(latestData.time) }}</td>
                  </tr>
                  <tr>
                      <td>最大值</td>
                      <td>{{ formatValue(stats.max_value) }} <span class="unit">{{ unit }}</span></td>
                  </tr>
                  <tr>
                      <td>最小值</td>
                      <td>{{ formatValue(stats.min_value) }} <span class="unit">{{ unit }}</span></td>
                  </tr>
                  <tr>
                      <td>平均值</td>
                      <td>{{ formatValue(stats.avg_value) }} <span class="unit">{{ unit }}</span></td>
                  </tr>
              </tbody>
          </table>

          <div class="divider"></div>

          <!-- 历史趋势图表 -->
          <div class="section-title">
            <span class="title-icon">📈</span>
            历史变化趋势
            <span class="chart-hint">（前{{ chartRange }}天）</span>
          </div>
          <div class="chart-container">
            <v-chart class="chart" :option="chartOption" autoresize />
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">📍</div>
          <p>请在左侧选择一个测点查看详情</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DataZoomComponent,
  MarkLineComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import api from '@/utils/api'

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DataZoomComponent,
  MarkLineComponent
])

const props = defineProps({
  pointCode: String,
  pointName: String,
  selectedTime: Date, // 从时间轴传入的选中时间
  chartRange: {
    type: Number,
    default: 7 // 默认显示7天
  }
})

const latestData = ref({})
const stats = ref({})
const historyData = ref([])
const allHistoryData = ref([]) // 存储完整历史数据

// 当前时间对应的值
const currentTimeValue = ref(null)

// Watch pointCode to auto-fetch
watch(() => props.pointCode, (newVal) => {
  if (newVal) {
    fetchData()
  } else {
    // 清空数据
    latestData.value = {}
    stats.value = {}
    historyData.value = []
    allHistoryData.value = []
    currentTimeValue.value = null
  }
}, { immediate: true })

// Watch selectedTime to update current value and filter chart data
watch(() => props.selectedTime, (newTime) => {
  if (newTime && allHistoryData.value.length > 0) {
    updateCurrentTimeValue(newTime)
    filterHistoryDataByTime(newTime)
  }
}, { immediate: true, deep: true })

// Watch chartRange to update chart
watch(() => props.chartRange, () => {
  if (props.selectedTime && allHistoryData.value.length > 0) {
    filterHistoryDataByTime(props.selectedTime)
  }
})

// 判断是否为水位测点
const isWaterLevel = computed(() => {
  return props.pointName && props.pointName.includes('水位')
})

// 单位判断：水位用 m，其他用 mm
const unit = computed(() => {
  return isWaterLevel.value ? 'm' : 'mm'
})

// 格式化数值（保留2位小数，避免过长）
const formatValue = (val) => {
  if (val === null || val === undefined) return '--'
  const num = parseFloat(val)
  if (isNaN(num)) return '--'
  return num.toFixed(2)
}

// 计算当前值与最新值的差异
const valueDiff = computed(() => {
  if (currentTimeValue.value === null || latestData.value.value === undefined) {
    return null
  }
  return currentTimeValue.value - latestData.value.value
})

const valueDiffClass = computed(() => {
  if (valueDiff.value === null) return ''
  if (valueDiff.value > 0) return 'positive'
  if (valueDiff.value < 0) return 'negative'
  return 'neutral'
})

const valueDiffText = computed(() => {
  if (valueDiff.value === null) return ''
  const sign = valueDiff.value >= 0 ? '+' : ''
  return `较最新值: ${sign}${valueDiff.value.toFixed(2)} ${unit.value}`
})

const formatDate = (str) => {
    if (!str) return '--'
    let date
    if (str instanceof Date) {
        date = str
    } else {
        date = new Date(str)
    }
    if (isNaN(date.getTime())) return '--'
    return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    })
}

// 根据选中时间找到最接近的监测值
const updateCurrentTimeValue = (selectedTime) => {
  if (!selectedTime || allHistoryData.value.length === 0) {
    currentTimeValue.value = null
    return
  }

  const targetTime = selectedTime.getTime()
  let closestData = null
  let minDiff = Infinity

  for (const item of allHistoryData.value) {
    const itemTime = new Date(item.time).getTime()
    // 找最接近选中时间的数据（不限制必须在之前）
    const diff = Math.abs(targetTime - itemTime)
    if (diff < minDiff) {
      minDiff = diff
      closestData = item
    }
  }

  currentTimeValue.value = closestData ? closestData.value : null
}

// 根据选中时间和chartRange过滤历史数据
const filterHistoryDataByTime = (selectedTime) => {
  if (!selectedTime || allHistoryData.value.length === 0) {
    historyData.value = allHistoryData.value.slice(-50)
    return
  }

  const targetTime = selectedTime.getTime()
  const rangeMs = props.chartRange * 24 * 60 * 60 * 1000 // chartRange天的毫秒数
  const startTime = targetTime - rangeMs

  // 筛选在时间范围内的数据
  const filteredData = allHistoryData.value.filter(item => {
    const itemTime = new Date(item.time).getTime()
    return itemTime >= startTime && itemTime <= targetTime
  })

  historyData.value = filteredData
}

const chartOption = computed(() => {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10, 25, 50, 0.95)',
      borderColor: '#00a0e9',
      textStyle: { color: '#fff', fontSize: 12 },
      formatter: (params) => {
        if (params.length > 0) {
          const data = historyData.value[params[0].dataIndex]
          const time = data ? formatDate(data.time) : ''
          return `<div style="font-weight:bold;">${time}</div>
                  <div>${isWaterLevel.value ? '水位' : '位移'}: <span style="color:#00e5ff;font-weight:bold;">${formatValue(params[0].value)}</span> ${unit.value}</div>`
        }
        return ''
      }
    },
    grid: {
      top: '8%',
      left: '3%',
      right: '4%',
      bottom: '12%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: historyData.value.map(item => {
        const date = new Date(item.time)
        return `${date.getMonth() + 1}/${date.getDate()}\n${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
      }),
      axisLine: { lineStyle: { color: 'rgba(0, 160, 233, 0.5)' } },
      axisLabel: { 
        color: '#fff',
        interval: 'auto', 
        fontSize: 9
      }
    },
    yAxis: {
      type: 'value',
      name: unit.value,
      nameTextStyle: { color: '#aaa', fontSize: 10 },
      axisLine: { lineStyle: { color: 'rgba(0, 160, 233, 0.5)' } },
      axisLabel: { color: '#fff', fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(0, 160, 233, 0.2)' } },
      scale: true
    },
    series: [
      {
        data: historyData.value.map(item => item.value),
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 3,
        showSymbol: historyData.value.length < 50,
        lineStyle: {
          color: '#00e5ff',
          width: 2
        },
        itemStyle: {
          color: '#00e5ff',
          borderColor: '#fff',
          borderWidth: 1
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(0, 229, 255, 0.5)' },
              { offset: 1, color: 'rgba(0, 229, 255, 0)' }
            ]
          }
        }
      }
    ]
  }
})

const fetchData = async () => {
  if (!props.pointCode) return
  
  try {
    const resLatest = await api.get(`/measurements/${props.pointCode}/latest`)
    latestData.value = resLatest.data
    
    const resStats = await api.get(`/measurements/${props.pointCode}/stats`)
    stats.value = resStats.data
    
    // 获取更多历史数据用于时间轴筛选（获取最近90天的数据）
    const resHistory = await api.get(`/measurements/${props.pointCode}`, {
      params: { limit: 1000 }
    })
    let data = resHistory.data
    
    // 按时间升序排序
    data.sort((a, b) => new Date(a.time) - new Date(b.time))
    allHistoryData.value = data
    
    // 根据当前选中时间更新数据
    if (props.selectedTime) {
      updateCurrentTimeValue(props.selectedTime)
      filterHistoryDataByTime(props.selectedTime)
    } else {
      historyData.value = data.slice(-50)
    }

  } catch (error) {
    console.error("Fetch point data error:", error)
    latestData.value = {}
    stats.value = {}
    historyData.value = []
    allHistoryData.value = []
    currentTimeValue.value = null
  }
}
</script>

<style scoped>
.sidebar-wrapper {
  position: absolute;
  right: 20px;
  top: 100px;
  bottom: 90px;
  width: 350px;
  transition: transform 0.3s;
  pointer-events: auto;
  z-index: 10;
}

.sidebar-wrapper.collapsed {
  transform: translateX(400px);
}

.sidebar-right {
  width: 100%;
  height: 100%;
  background: rgba(10, 25, 50, 0.8);
  border: 1px solid rgba(0, 160, 233, 0.3);
  box-shadow: 0 0 35px rgba(0, 160, 233, 0.5);
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
  border-radius: 8px;
}

.panel-header {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 160, 233, 0.1);
  border-bottom: 1px solid rgba(0, 160, 233, 0.3);
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  padding: 0 10px;
}

.title {
  color: #00e5ff;
  font-size: 18px;
  font-weight: bold;
}

.bind-btn {
  background: transparent;
  border: 1px solid #00e5ff;
  color: #00e5ff;
  border-radius: 4px;
  cursor: pointer;
  margin-left: auto;
  padding: 2px 8px;
}

.bind-btn:hover {
  background: rgba(0, 229, 255, 0.2);
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.section-title {
  color: #fff;
  font-size: 14px;
  margin-bottom: 10px;
  border-left: 3px solid #00e5ff;
  padding-left: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.title-icon {
  font-size: 14px;
}

.chart-hint {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-left: auto;
}

/* 当前值卡片 */
.current-value-card {
  background: linear-gradient(135deg, rgba(0, 160, 233, 0.2), rgba(0, 229, 255, 0.1));
  border: 1px solid rgba(0, 160, 233, 0.4);
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  margin-bottom: 15px;
  box-shadow: 0 0 20px rgba(0, 160, 233, 0.2);
}

.value-main {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 5px;
}

.value-number {
  font-size: 28px;
  font-weight: bold;
  color: #00e5ff;
  text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}

.value-unit {
  font-size: 14px;
  color: #aaa;
}

.value-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 5px;
}

.value-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 3px;
}

.value-diff {
  font-size: 11px;
  margin-top: 8px;
  padding: 3px 8px;
  border-radius: 10px;
  display: inline-block;
}

.value-diff.positive {
  background: rgba(255, 77, 79, 0.2);
  color: #ff6b6b;
}

.value-diff.negative {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.value-diff.neutral {
  background: rgba(255, 255, 255, 0.1);
  color: #888;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.data-table th, .data-table td {
  padding: 6px 8px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: #ccc;
  font-size: 12px;
}

.data-table th {
  color: #00e5ff;
}

.data-table .value {
  color: #00e5ff;
  font-weight: bold;
  font-size: 13px;
}

.unit {
  font-size: 10px;
  color: #aaa;
  margin-left: 2px;
}

.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 12px 0;
}

.chart-container {
  height: 200px;
  width: 100%;
}

.chart {
  height: 100%;
  width: 100%;
}

.empty-state {
  text-align: center;
  color: #aaa;
  margin-top: 80px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

/* 隐形滚动条样式 - 和左侧统一 */
.panel-content::-webkit-scrollbar {
  width: 4px;
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
