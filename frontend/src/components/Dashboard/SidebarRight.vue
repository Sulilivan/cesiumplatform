<template>
  <div class="sidebar-right" :class="{ 'collapsed': !pointCode }">
    <div class="panel-header">
      <div class="title">{{ pointName || '测点详情' }}</div>
    </div>
    
    <div class="panel-content">
      <div v-if="pointCode">
        <!-- 实时数据表格 -->
        <div class="section-title">实时监测数据</div>
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
                    <td class="value">{{ latestData.value !== undefined ? latestData.value : '--' }} <span class="unit">{{ unit }}</span></td>
                </tr>
                <tr>
                    <td>监测时间</td>
                    <td>{{ formatDate(latestData.time) }}</td>
                </tr>
                <tr>
                    <td>最大值</td>
                    <td>{{ stats.max_value !== undefined ? stats.max_value : '--' }} <span class="unit">{{ unit }}</span></td>
                </tr>
                <tr>
                    <td>最小值</td>
                    <td>{{ stats.min_value !== undefined ? stats.min_value : '--' }} <span class="unit">{{ unit }}</span></td>
                </tr>
                <tr>
                    <td>平均值</td>
                    <td>{{ stats.avg_value ? stats.avg_value.toFixed(2) : '--' }} <span class="unit">{{ unit }}</span></td>
                </tr>
            </tbody>
        </table>

        <div class="divider"></div>

        <!-- 历史趋势图表 -->
        <div class="section-title">历史变化趋势</div>
        <div class="chart-container">
          <v-chart class="chart" :option="chartOption" autoresize />
        </div>
      </div>
      <div v-else class="empty-state">
        <p>请在左侧选择一个测点查看详情</p>
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
  DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import api from '@/utils/api'

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DataZoomComponent
])

const props = defineProps({
  pointCode: String,
  pointName: String
})

const latestData = ref({})
const stats = ref({})
const historyData = ref([])

// 判断是否为水位测点
const isWaterLevel = computed(() => {
  return props.pointName && props.pointName.includes('水位')
})

// 单位判断：水位用 m，其他用 mm
const unit = computed(() => {
  return isWaterLevel.value ? 'm' : 'mm'
})

const formatDate = (str) => {
    if (!str) return '--'
    return new Date(str).toLocaleString()
}

const chartOption = computed(() => {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10, 25, 50, 0.9)',
      borderColor: '#00a0e9',
      textStyle: { color: '#fff' }
    },
    grid: {
      top: '10%',
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: historyData.value.map(item => {
        const date = new Date(item.time)
        return `${date.getMonth() + 1}-${date.getDate()}\n${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
      }),
      axisLine: { lineStyle: { color: 'rgba(0, 160, 233, 0.5)' } },
      axisLabel: { 
        color: '#fff',
        interval: 'auto', 
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      name: unit.value, // 显示单位
      nameTextStyle: { color: '#aaa' },
      axisLine: { lineStyle: { color: 'rgba(0, 160, 233, 0.5)' } },
      axisLabel: { color: '#fff' },
      splitLine: { lineStyle: { color: 'rgba(0, 160, 233, 0.2)' } },
      scale: true
    },
    series: [
      {
        data: historyData.value.map(item => item.value),
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#00e5ff',
          width: 2
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
    // 1. 获取最新数据
    const resLatest = await api.get(`/measurements/${props.pointCode}/latest`)
    latestData.value = resLatest.data
    
    // 2. 获取统计数据
    const resStats = await api.get(`/measurements/${props.pointCode}/stats`)
    stats.value = resStats.data
    
    // 3. 获取历史数据 (最近 20 条用于绘图) - API 可能需要 limit 支持，暂取全部然后截取
    // 注意：这里使用的是 range 接口或者默认的 measurements 列表接口
    // 假设后端 /measurements/{code} 返回列表
    const resHistory = await api.get(`/measurements/${props.pointCode}`)
    // 取最近 50 条并反转顺序（如果是降序返回）若后端是升序则直接用
    // 假设后端是按时间排序的
    let data = resHistory.data
    // 如果数据量太大，截取一部分
    if (data.length > 50) {
        data = data.slice(data.length - 50) 
    }
    historyData.value = data

  } catch (error) {
    console.error("Fetch point data error:", error)
    // 重置数据
    latestData.value = {}
    stats.value = {}
    historyData.value = []
  }
}

watch(() => props.pointCode, (newVal) => {
  if (newVal) {
    fetchData()
  }
}, { immediate: true })

</script>

<style scoped>
.sidebar-right {
  position: absolute;
  right: 20px;
  top: 100px;
  bottom: 20px;
  width: 350px;
  background: rgba(10, 25, 50, 0.8);
  border: 1px solid rgba(0, 160, 233, 0.3);
  box-shadow: 0 0 35px rgba(0, 160, 233, 0.5);
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
  transition: transform 0.3s ease-in-out;
  border-radius: 12px; /* 圆角 - 需求 3 */
}

.sidebar-right.collapsed {
  transform: translateX(400px); /* 移出屏幕 */
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
}

.title {
  color: #00e5ff;
  font-size: 18px;
  font-weight: bold;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.section-title {
  color: #fff;
  font-size: 14px;
  margin-bottom: 10px;
  border-left: 3px solid #00e5ff;
  padding-left: 10px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.data-table th, .data-table td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: #ccc;
  font-size: 14px;
}

.data-table th {
  color: #00e5ff;
}

.data-table .value {
  color: #00e5ff;
  font-weight: bold;
  font-size: 16px;
}

.unit {
  font-size: 12px;
  color: #aaa;
  margin-left: 4px;
}

.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 20px 0;
}

.chart-container {
  height: 250px;
  width: 100%;
}

.chart {
  height: 100%;
  width: 100%;
}

.empty-state {
  text-align: center;
  color: #aaa;
  margin-top: 50px;
}
</style>
