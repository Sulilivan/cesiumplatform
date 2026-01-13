<template>
  <div class="bottom-bar">
    <div class="bar-content">
        <!-- 左侧状态信息 -->
        <div class="status-section">
            <div class="info-item">
                <span class="label">系统状态：</span>
                <span class="value normal">运行正常</span>
            </div>
            <div class="info-item">
                <span class="label">当前坐标：</span>
                <span class="value">{{ coords }}</span>
            </div>
        </div>

        <!-- 中间时间轴控制区 -->
        <div class="timeline-section">
            <!-- 年月日滚轮选择器 -->
            <div class="date-wheel-group">
                <div class="wheel-item">
                    <div class="wheel-label">年</div>
                    <div class="wheel-control" @wheel.prevent="adjustYear">
                        <button class="wheel-btn" @click="adjustYear({deltaY: -1})">▲</button>
                        <span class="wheel-value">{{ selectedYear }}</span>
                        <button class="wheel-btn" @click="adjustYear({deltaY: 1})">▼</button>
                    </div>
                </div>
                <div class="wheel-item">
                    <div class="wheel-label">月</div>
                    <div class="wheel-control" @wheel.prevent="adjustMonth">
                        <button class="wheel-btn" @click="adjustMonth({deltaY: -1})">▲</button>
                        <span class="wheel-value">{{ String(selectedMonth).padStart(2, '0') }}</span>
                        <button class="wheel-btn" @click="adjustMonth({deltaY: 1})">▼</button>
                    </div>
                </div>
                <div class="wheel-item">
                    <div class="wheel-label">日</div>
                    <div class="wheel-control" @wheel.prevent="adjustDay">
                        <button class="wheel-btn" @click="adjustDay({deltaY: -1})">▲</button>
                        <span class="wheel-value">{{ String(selectedDay).padStart(2, '0') }}</span>
                        <button class="wheel-btn" @click="adjustDay({deltaY: 1})">▼</button>
                    </div>
                </div>
            </div>

            <!-- 24小时时间滑块 -->
            <div class="time-slider-group">
                <span class="time-label">00:00</span>
                <div class="slider-container">
                    <input 
                        type="range" 
                        v-model.number="timeSliderValue" 
                        min="0" 
                        max="1439"
                        step="1"
                        class="time-slider"
                        @input="onSliderChange"
                    />
                    <div class="slider-track">
                        <div class="slider-progress" :style="{ width: (timeSliderValue / 1439 * 100) + '%' }"></div>
                    </div>
                    <!-- 时刻刻度 -->
                    <div class="slider-ticks">
                        <div class="tick-mark" style="left: 0%"><div class="tick-line"></div></div>
                        <div class="tick-mark" style="left: 25%"><div class="tick-line"></div><div class="tick-label">06:00</div></div>
                        <div class="tick-mark" style="left: 50%"><div class="tick-line"></div><div class="tick-label">12:00</div></div>
                        <div class="tick-mark" style="left: 75%"><div class="tick-line"></div><div class="tick-label">18:00</div></div>
                        <div class="tick-mark" style="left: 100%"><div class="tick-line"></div></div>
                    </div>
                </div>
                <span class="time-label">23:59</span>
                <span class="current-time-display">{{ formattedTime }}</span>
            </div>

            <!-- 快捷按钮 -->
            <div class="quick-buttons">
                <button 
                    class="quick-btn range-btn" 
                    :class="{ active: chartRange === 7 }"
                    @click="setChartRange(7)" 
                    title="图表显示前7天数据"
                >7天</button>
                <button 
                    class="quick-btn range-btn" 
                    :class="{ active: chartRange === 30 }"
                    @click="setChartRange(30)" 
                    title="图表显示前30天数据"
                >30天</button>
                <button 
                    class="quick-btn range-btn" 
                    :class="{ active: chartRange === 90 }"
                    @click="setChartRange(90)" 
                    title="图表显示前90天数据"
                >90天</button>
                <button 
                    class="quick-btn range-btn" 
                    :class="{ active: chartRange === 365 }"
                    @click="setChartRange(365)" 
                    title="图表显示前365天数据"
                >1年</button>
                <button class="quick-btn now-btn" @click="setToNow" title="跳转到当前时间">
                    <span class="btn-icon">⏱</span> 当前
                </button>
                <button class="quick-btn speed-btn" @click="toggleSpeed" title="切换播放速度">
                    <span class="btn-icon">⚡</span> {{ playSpeed }}x
                </button>
                <button class="quick-btn" @click="playTimeline" :class="{ active: isPlaying }" title="播放时间轴">
                    <span class="btn-icon">{{ isPlaying ? '⏸' : '▶' }}</span>
                </button>
            </div>
        </div>

        <!-- 右侧选中时间显示 -->
        <div class="selected-time-section">
            <div class="info-item">
                <span class="label">选中时间：</span>
                <span class="value highlight">{{ fullSelectedTimeDisplay }}</span>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
    coords: String,
    modelValue: Date, // 双向绑定的时间值
    chartRange: {
        type: Number,
        default: 7
    }
})

const emit = defineEmits(['update:modelValue', 'update:chartRange', 'timeChange'])

// 当前时间
const now = new Date()

// 选中的日期
const selectedYear = ref(now.getFullYear())
const selectedMonth = ref(now.getMonth() + 1)
const selectedDay = ref(now.getDate())

// 时间滑块值（0-1439，代表一天的分钟数）
const timeSliderValue = ref(now.getHours() * 60 + now.getMinutes())

// 图表时间范围（天数）
const chartRange = ref(props.chartRange)

// 播放状态
const isPlaying = ref(false)
let playTimer = null

// 播放速度
const playSpeed = ref(1)
const speedOptions = [1, 2, 5, 10, 20]

// 切换播放速度
const toggleSpeed = () => {
    const currentIndex = speedOptions.indexOf(playSpeed.value)
    const nextIndex = (currentIndex + 1) % speedOptions.length
    playSpeed.value = speedOptions[nextIndex]
}

// 计算当月天数
const daysInMonth = computed(() => {
    return new Date(selectedYear.value, selectedMonth.value, 0).getDate()
})

// 格式化时间显示（时分）
const formattedTime = computed(() => {
    const hours = Math.floor(timeSliderValue.value / 60)
    const minutes = timeSliderValue.value % 60
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
})

// 完整选中时间显示（北京时间格式）
const fullSelectedTimeDisplay = computed(() => {
    const date = getSelectedDateTime()
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    })
})

// 获取完整的选中时间
const getSelectedDateTime = () => {
    const hours = Math.floor(timeSliderValue.value / 60)
    const minutes = timeSliderValue.value % 60
    return new Date(
        selectedYear.value,
        selectedMonth.value - 1,
        selectedDay.value,
        hours,
        minutes,
        0
    )
}

// 年份滚轮调整
const adjustYear = (event) => {
    const delta = event.deltaY > 0 ? -1 : 1
    const newYear = selectedYear.value + delta
    if (newYear >= 2020 && newYear <= 2030) {
        selectedYear.value = newYear
        validateDay()
        emitSelectedTime()
    }
}

// 月份滚轮调整
const adjustMonth = (event) => {
    const delta = event.deltaY > 0 ? -1 : 1
    let newMonth = selectedMonth.value + delta
    if (newMonth < 1) {
        newMonth = 12
        selectedYear.value--
    } else if (newMonth > 12) {
        newMonth = 1
        selectedYear.value++
    }
    selectedMonth.value = newMonth
    validateDay()
    emitSelectedTime()
}

// 日期滚轮调整
const adjustDay = (event) => {
    const delta = event.deltaY > 0 ? -1 : 1
    let newDay = selectedDay.value + delta
    const maxDay = daysInMonth.value
    if (newDay < 1) {
        newDay = maxDay
    } else if (newDay > maxDay) {
        newDay = 1
    }
    selectedDay.value = newDay
    emitSelectedTime()
}

// 验证日期有效性
const validateDay = () => {
    const maxDay = daysInMonth.value
    if (selectedDay.value > maxDay) {
        selectedDay.value = maxDay
    }
}

// 滑块改变时
const onSliderChange = () => {
    emitSelectedTime()
}

// 发射选中时间
const emitSelectedTime = () => {
    const selectedTime = getSelectedDateTime()
    emit('update:modelValue', selectedTime)
    emit('timeChange', selectedTime)
}

// 设置图表时间范围
const setChartRange = (days) => {
    chartRange.value = days
    emit('update:chartRange', days)
}

// 设置为当前时间
const setToNow = () => {
    const now = new Date()
    selectedYear.value = now.getFullYear()
    selectedMonth.value = now.getMonth() + 1
    selectedDay.value = now.getDate()
    timeSliderValue.value = now.getHours() * 60 + now.getMinutes()
    emitSelectedTime()
}

// 播放/暂停时间轴（跨天连续播放）
const playTimeline = () => {
    isPlaying.value = !isPlaying.value
    if (isPlaying.value) {
        playTimer = setInterval(() => {
            // 每次前进 5分钟 * 倍速
            const step = 5 * playSpeed.value
            let newValue = timeSliderValue.value + step
            
            if (newValue > 1439) {
                // 如果超过23:59，进入下一天
                const excessMinutes = newValue - 1440
                
                // 日期加1天
                const nextDayDate = new Date(selectedYear.value, selectedMonth.value - 1, selectedDay.value + 1)
                selectedYear.value = nextDayDate.getFullYear()
                selectedMonth.value = nextDayDate.getMonth() + 1
                selectedDay.value = nextDayDate.getDate()
                
                // 设置新时间（从00:00 + 剩余分钟开始）
                timeSliderValue.value = excessMinutes
            } else {
                // 当天内继续播放
                timeSliderValue.value = newValue
            }
            
            emitSelectedTime()
        }, 50) // 50ms更新一次，保持流畅
    } else {
        if (playTimer) {
            clearInterval(playTimer)
            playTimer = null
        }
    }
}

// 监听外部传入的时间值
watch(() => props.modelValue, (newVal) => {
    if (newVal instanceof Date && !isNaN(newVal)) {
        selectedYear.value = newVal.getFullYear()
        selectedMonth.value = newVal.getMonth() + 1
        selectedDay.value = newVal.getDate()
        timeSliderValue.value = newVal.getHours() * 60 + newVal.getMinutes()
    }
}, { immediate: true })

// 监听外部传入的chartRange
watch(() => props.chartRange, (newVal) => {
    chartRange.value = newVal
})

// 暴露方法供外部调用
defineExpose({
    getSelectedDateTime,
    setToNow
})

onMounted(() => {
    // 初始化时发射当前选中时间
    emitSelectedTime()
})

onUnmounted(() => {
    if (playTimer) {
        clearInterval(playTimer)
    }
})
</script>

<style scoped>
.bottom-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: rgba(10, 25, 50, 0.95);
  border-top: 1px solid rgba(0, 160, 233, 0.5);
  display: flex;
  align-items: center;
  padding: 0 20px;
  z-index: 100;
  color: #fff;
  font-size: 13px;
  backdrop-filter: blur(10px);
}

.bar-content {
  display: flex;
  align-items: center;
  width: 100%;
  justify-content: space-between;
}

/* 状态区域 */
.status-section {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex-shrink: 0;
  min-width: 180px;
}

/* 时间轴控制区 */
.timeline-section {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
  justify-content: center;
}

/* 年月日滚轮选择器 */
.date-wheel-group {
  display: flex;
  gap: 4px;
}

.wheel-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.wheel-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 2px;
}

.wheel-control {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(0, 160, 233, 0.1);
  border: 1px solid rgba(0, 160, 233, 0.3);
  border-radius: 4px;
  padding: 2px;
  cursor: ns-resize;
}

.wheel-btn {
  background: transparent;
  border: none;
  color: rgba(0, 229, 255, 0.6);
  cursor: pointer;
  font-size: 8px;
  padding: 0;
  line-height: 1;
  transition: color 0.2s;
}

.wheel-btn:hover {
  color: #00e5ff;
}

.wheel-value {
  font-size: 14px;
  font-weight: bold;
  color: #00e5ff;
  min-width: 36px;
  text-align: center;
  user-select: none;
}

/* 时间滑块组 */
.time-slider-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  max-width: 400px;
  min-width: 280px;
}

.time-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
}

.slider-container {
  position: relative;
  flex: 1;
  height: 36px;
  display: flex;
  align-items: center;
}

.time-slider {
  position: absolute;
  width: 100%;
  height: 8px;
  -webkit-appearance: none;
  appearance: none;
  background: transparent;
  cursor: pointer;
  z-index: 3;
  top: 50%;
  transform: translateY(-50%);
  margin-top: -4px;
}

.time-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #00e5ff;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.8);
  transition: transform 0.15s;
}

.time-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.time-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #00e5ff;
  border-radius: 50%;
  cursor: pointer;
  border: none;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.8);
}

.slider-track {
  position: absolute;
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  z-index: 1;
  top: 50%;
  transform: translateY(-50%);
  margin-top: -4px;
}

.slider-progress {
  height: 100%;
  background: linear-gradient(90deg, rgba(0, 160, 233, 0.6), #00e5ff);
  border-radius: 2px;
  transition: width 0.05s;
}

/* 刻度标记 */
.slider-ticks {
  position: absolute;
  width: 100%;
  bottom: 0;
  z-index: 0;
}

.tick-mark {
  position: absolute;
  transform: translateX(-50%);
}

.tick-line {
  width: 1px;
  height: 4px;
  background: rgba(0, 160, 233, 0.4);
  margin: 0 auto;
}

.tick-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.4);
  text-align: center;
  margin-top: 1px;
}

.current-time-display {
  font-size: 14px;
  font-weight: bold;
  color: #00e5ff;
  background: rgba(0, 160, 233, 0.15);
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid rgba(0, 160, 233, 0.3);
  min-width: 50px;
  text-align: center;
}

/* 快捷按钮 */
.quick-buttons {
  display: flex;
  gap: 4px;
}

.quick-btn {
  background: rgba(0, 160, 233, 0.15);
  border: 1px solid rgba(0, 160, 233, 0.4);
  color: #00e5ff;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 3px;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: rgba(0, 160, 233, 0.3);
  border-color: rgba(0, 160, 233, 0.6);
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
}

.quick-btn.active {
  background: rgba(0, 229, 255, 0.3);
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.5);
}

.quick-btn.range-btn {
  min-width: 36px;
  padding: 5px 8px;
}

.quick-btn.speed-btn {
  min-width: 45px;
  color: #ff9800; /* 橙色以区分 */
  border-color: rgba(255, 152, 0, 0.4);
  background: rgba(255, 152, 0, 0.15);
}

.quick-btn.speed-btn:hover {
  background: rgba(255, 152, 0, 0.3);
  box-shadow: 0 0 10px rgba(255, 152, 0, 0.4);
}

.quick-btn.now-btn {
  background: rgba(255, 235, 59, 0.15);
  border-color: rgba(255, 235, 59, 0.4);
  color: #ffeb3b;
}

.quick-btn.now-btn:hover {
  background: rgba(255, 235, 59, 0.3);
  box-shadow: 0 0 10px rgba(255, 235, 59, 0.4);
}

.btn-icon {
  font-size: 11px;
}

/* 选中时间区域 */
.selected-time-section {
  flex-shrink: 0;
  min-width: 180px;
  text-align: right;
}

/* 通用样式 */
.info-item {
  display: flex;
  align-items: center;
}

.label {
  color: rgba(255,255,255,0.6);
  margin-right: 5px;
  font-size: 12px;
}

.value {
  color: #00e5ff;
  font-size: 12px;
}

.value.normal {
  color: #00ff00;
}

.value.highlight {
  background: rgba(0, 160, 233, 0.15);
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid rgba(0, 160, 233, 0.3);
  font-weight: bold;
}
</style>
