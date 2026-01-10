<template>
  <div class="bottom-bar">
    <div class="bar-content">
        <div class="info-item">
            <span class="label">系统状态：</span>
            <span class="value normal">运行正常</span>
        </div>
        <div class="info-item">
            <span class="label">数据最后更新：</span>
            <span class="value">{{ lastUpdateTime }}</span>
        </div>
        <div class="info-item">
            <span class="label">当前坐标：</span>
            <span class="value">{{ coords }}</span>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
    coords: String
})

const lastUpdateTime = ref(new Date().toLocaleString())
let timer = null

onMounted(() => {
    timer = setInterval(() => {
        lastUpdateTime.value = new Date().toLocaleString()
    }, 5000) // 这里模拟数据更新时间
})

onUnmounted(() => {
    if(timer) clearInterval(timer)
})
</script>

<style scoped>
.bottom-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  background: rgba(10, 25, 50, 0.9);
  border-top: 1px solid rgba(0, 160, 233, 0.5);
  display: flex;
  align-items: center;
  padding: 0 20px;
  z-index: 100;
  color: #fff;
  font-size: 13px;
}

.bar-content {
  display: flex;
  gap: 30px;
  width: 100%;
}

.info-item {
  display: flex;
  align-items: center;
}

.label {
  color: rgba(255,255,255,0.6);
  margin-right: 5px;
}

.value {
  color: #00e5ff;
}

.value.normal {
  color: #00ff00;
}
</style>
