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
                    <td>最新水位</td>
                    <td class="value">{{ latestData.value || '--' }} m</td>
                </tr>
                <tr>
                    <td>监测时间</td>
                    <td>{{ formatDate(latestData.time) }}</td>
                </tr>
                <tr>
                    <td>最大值</td>
                    <td>{{ stats.max_value || '--' }} m</td>
                </tr>
                <tr>
                    <td>最小值</td>
                    <td>{{ stats.min_value || '--' }} m</td>
                </tr>
                <tr>
                    <td>平均值</td>
                    <td>{{ stats.avg_value ? stats.avg_value.toFixed(2) : '--' }} m</td>
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
      data: historyData.value.map(item => new Date(item.time).toLocaleTimeString()),
      axisLine: { lineStyle: { color: 'rgba(0, 160, 233, 0.5)' } },
      axisLabel: { color: '#fff' }
    },
    yAxis: {
      type: 'value',
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
    ],
    dataZoom: [
        {
            type: 'inside',
            start: 0,
            end: 100
        }
    ]
  }
})

const fetchDetail = async (code) => {
    if(!code) return
    try {
        // 获取最新值
        const resLatest = await api.get(`/measurements/${code}/latest`)
        latestData.value = resLatest.data

        // 获取统计
        const resStats = await api.get(`/measurements/${code}/stats`)
        stats.value = resStats.data

        // 获取历史数据（这里可能需要限制数量或时间范围，这里简单获取全部或者最近的）
        // 实际上后端 /measurements/{code} 如果数据量大需要分页或时间筛选
        const resHistory = await api.get(`/measurements/${code}`)
        historyData.value = resHistory.data.slice(-50) // 取最后50条
    } catch (e) {
        console.error('Fetch detail failed', e)
        latestData.value = {}
        stats.value = {}
        historyData.value = []
    }
}

watch(() => props.pointCode, (newCode) => {
    if (newCode) {
        fetchDetail(newCode)
    } else {
        latestData.value = {}
        stats.value = {}
        historyData.value = []
    }
}, { immediate: true })

</script>

<style scoped>
.sidebar-right {
  position: absolute;
  right: 20px;
  top: 80px;
  width: 320px;
  bottom: 120px;
  background: rgba(10, 25, 50, 0.7);
  border: 1px solid rgba(0, 160, 233, 0.3);
  backdrop-filter: blur(10px);
  color: #fff;
  display: flex;
  flex-direction: column;
  z-index: 100;
  box-shadow: 0 0 20px rgba(0, 160, 233, 0.2) inset;  transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
}

.sidebar-right.collapsed {
  transform: translateX(340px); /* 移出屏幕 */
  opacity: 0;
  pointer-events: none;}

.panel-header {
  height: 40px;
  background: rgba(0, 160, 233, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(0, 160, 233, 0.5);
}

.title {
  font-weight: bold;
  color: #00e5ff;
}

.panel-content {
  padding: 15px;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: 14px;
  border-left: 3px solid #00e5ff;
  padding-left: 8px;
  margin-bottom: 10px;
  color: #cceeff;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin-bottom: 15px;
}

.data-table th, .data-table td {
  border: 1px solid rgba(0, 160, 233, 0.3);
  padding: 8px;
  text-align: left;
}

.data-table th {
  background: rgba(0, 160, 233, 0.2);
  color: #00e5ff;
}

.value {
  color: #00ff00;
  font-family: 'Courier New', Courier, monospace;
  font-weight: bold;
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
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.5);
}

.divider {
  height: 1px;
  background: rgba(0, 160, 233, 0.3);
  margin: 15px 0;
}
</style>
