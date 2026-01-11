<template>
  <div class="admin-container">
    <div class="admin-sidebar">
      <div class="sidebar-title">系统管理</div>
      <div 
        class="menu-item" 
        :class="{ active: currentTab === 'users' }"
        @click="currentTab = 'users'"
      >
        用户管理
      </div>
      <div 
        class="menu-item" 
        :class="{ active: currentTab === 'points' }"
        @click="currentTab = 'points'"
      >
        测点管理
      </div>
      <div 
        class="menu-item" 
        :class="{ active: currentTab === 'data' }"
        @click="currentTab = 'data'"
      >
        数据中心
      </div>
      <div class="menu-item back-btn" @click="goBack">
        &lt; 返回地图
      </div>
    </div>
    
    <div class="admin-content">
      <!-- 用户管理面板 -->
      <div v-if="currentTab === 'users'" class="panel">
        <div class="panel-header">
          <h2>用户管理</h2>
          <button class="btn-primary" @click="openUserModal(null)">添加用户</button>
        </div>
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.email }}</td>
              <td>
                <span :class="user.role === 'admin' ? 'tag-admin' : 'tag-user'">
                  {{ user.role }}
                </span>
              </td>
              <td>{{ user.is_active ? '激活' : '禁用' }}</td>
              <td>
                <button class="btn-edit" @click="openUserModal(user)">编辑</button>
                <button 
                  v-if="user.username !== 'admin'" 
                  class="btn-danger" 
                  @click="deleteUser(user.id)"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 测点管理面板 -->
      <div v-if="currentTab === 'points'" class="panel">
        <div class="panel-header">
          <h2>测点管理</h2>
          <div class="header-actions">
            <div class="filter-group">
              <label>分类筛选：</label>
              <select v-model="pointTypeFilter" class="filter-select">
                <option value="">全部类型</option>
                <option value="倒垂线">倒垂线</option>
                <option value="引张线">引张线</option>
                <option value="静力水准">静力水准</option>
                <option value="水位">水位</option>
              </select>
            </div>
            <button class="btn-primary" @click="openPointModal(null)">添加测点</button>
          </div>
        </div>
        <table class="admin-table">
          <thead>
            <tr>
              <th>编号</th>
              <th>名称</th>
              <th>类型</th>
              <th>经度</th>
              <th>纬度</th>
              <th>高程</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="point in filteredPoints" :key="point.point_code">
              <td>{{ point.point_code }}</td>
              <td>{{ point.point_name }}</td>
              <td>{{ point.device_type }}</td>
              <td>{{ point.longitude }}</td>
              <td>{{ point.latitude }}</td>
              <td>{{ point.height }}</td>
              <td>
                <button class="btn-edit" @click="openPointModal(point)">编辑</button>
                <button class="btn-danger" @click="deletePoint(point.point_code)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 数据中心面板 -->
      <div v-if="currentTab === 'data'" class="panel">
        <div class="panel-header" style="flex-direction: column; align-items: flex-start;">
          <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 10px;">
              <h2>数据中心</h2>
              <div class="view-mode-toggle">
                  <button :class="{active: viewMode==='table'}" @click="switchView('table')" class="toggle-btn">表格</button>
                  <button :class="{active: viewMode==='chart'}" @click="switchView('chart')" class="toggle-btn">图表</button>
              </div>
          </div>
          <div class="header-actions" style="width: 100%; flex-wrap: wrap;">
            <div class="filter-group">
              <label>时间:</label>
              <input type="datetime-local" v-model="dataFilters.startTime" class="filter-input">
              <span>至</span>
              <input type="datetime-local" v-model="dataFilters.endTime" class="filter-input">
              
              <select v-model="dataFilters.type" class="filter-select" @change="dataFilters.name = ''">
                <option value="">全部类型</option>
                <option value="倒垂线">倒垂线</option>
                <option value="引张线">引张线</option>
                <option value="静力水准">静力水准</option>
                <option value="水位">水位</option>
              </select>
              
              <select v-model="dataFilters.name" class="filter-select" style="min-width: 150px;">
                  <option value="">全部测点</option>
                  <option v-for="p in filteredPointsForData" :key="p.point_code" :value="p.point_name">
                      {{ p.point_name }}
                  </option>
              </select>

              <button class="btn-primary" @click="fetchData">查询</button>
              <button class="btn-primary" @click="openDataModal(null)">添加数据</button>
            </div>
          </div>
        </div>
        
        <!-- Table View -->
        <div v-if="viewMode === 'table'">
           <div style="margin-bottom: 10px; color: #666; font-size: 14px;">
               共 {{ totalCount }} 条数据，当前第 {{ currentPage }} 页
           </div>
           <table class="admin-table">
             <thead>
                 <tr>
                     <th>ID</th>
                     <th>测点编号</th>
                     <th>测点名称</th>
                     <th>类型</th>
                     <th>监测值</th>
                     <th>时间</th>
                     <th>操作</th>
                 </tr>
             </thead>
             <tbody>
                 <tr v-for="d in measurements" :key="d.id">
                     <td>{{d.id}}</td>
                     <td>{{d.point_code}}</td>
                     <td>{{d.point_name}}</td>
                     <td>{{d.device_type}}</td>
                     <td>{{d.value}}</td>
                     <td>{{ formatDate(d.time) }}</td>
                     <td>
                         <button class="btn-edit" @click="openDataModal(d)">编辑</button>
                         <button class="btn-danger" @click="deleteData(d.id)">删除</button>
                     </td>
                 </tr>
             </tbody>
           </table>
           <div class="pagination" style="margin-top: 16px; display: flex; gap: 10px; align-items: center;">
               <button class="btn-primary" :disabled="currentPage <= 1" @click="changePage(-1)">上一页</button>
               <span>第 {{ currentPage }} 页</span>
               <button class="btn-primary" :disabled="measurements.length < pageSize" @click="changePage(1)">下一页</button>
           </div>
        </div>
        
        <!-- Chart View -->
        <div v-if="viewMode === 'chart'" class="chart-wrapper">
           <div ref="chartDiv" style="width: 100%; height: 500px;"></div>
        </div>
      </div>
    </div>

    <div v-if="showUserModal" class="modal-overlay">
      <div class="modal">
        <h3>{{ isEditingUser ? '编辑用户' : '添加用户' }}</h3>
        <form @submit.prevent="saveUser">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="userForm.username" :disabled="isEditingUser" required>
          </div>
          <div class="form-group" v-if="!isEditingUser">
            <label>密码</label>
            <input type="password" v-model="userForm.password" required>
          </div>
           <div class="form-group" v-if="isEditingUser">
            <label>重置密码 (留空如果不修改)</label>
            <input type="password" v-model="userForm.password">
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input type="email" v-model="userForm.email" required>
          </div>
          <div class="form-group">
            <label>角色</label>
            <select v-model="userForm.role">
                <option value="user">普通用户</option>
                <option value="admin">管理员</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showUserModal = false">取消</button>
            <button type="submit" class="btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 测点编辑/添加弹窗 -->
    <div v-if="showPointModal" class="modal-overlay">
      <div class="modal">
        <h3>{{ isEditing ? '编辑测点' : '添加测点' }}</h3>
        <form @submit.prevent="savePoint">
          <div class="form-group">
            <label>测点编号 (不可改)</label>
            <input v-model="pointForm.point_code" :disabled="isEditing" required>
          </div>
          <div class="form-group">
            <label>测点名称</label>
            <input v-model="pointForm.point_name" required>
          </div>
          <div class="form-group">
            <label>设备类型</label>
            <select v-model="pointForm.device_type" required>
              <option value="倒垂线">倒垂线</option>
              <option value="引张线">引张线</option>
              <option value="静力水准">静力水准</option>
              <option value="水位">水位</option>
            </select>
          </div>
          <div class="form-group">
            <label>经度</label>
            <input type="number" step="any" v-model.number="pointForm.longitude" required>
          </div>
          <div class="form-group">
            <label>纬度</label>
            <input type="number" step="any" v-model.number="pointForm.latitude" required>
          </div>
          <div class="form-group">
            <label>高程</label>
            <input type="number" step="any" v-model.number="pointForm.height" required>
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="showPointModal = false">取消</button>
            <button type="submit" class="btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 数据编辑/添加弹窗 -->
    <div v-if="showDataModal" class="modal-overlay">
      <div class="modal">
        <h3>{{ isDataEditing ? '编辑数据' : '添加数据' }}</h3>
        <form @submit.prevent="saveData">
          <div class="form-group">
            <label>测点编号 ({{ isDataEditing ? '不可改' : '请选择' }})</label>
            <input v-if="isDataEditing" v-model="dataForm.point_code" disabled>
            <select v-else v-model="dataForm.point_code" required>
                <option v-for="p in points" :key="p.point_code" :value="p.point_code">
                    {{p.point_name}} ({{p.point_code}})
                </option>
            </select>
          </div>
          <div class="form-group">
             <label>监测值</label>
             <input type="number" step="any" v-model.number="dataForm.value" required>
          </div>
          <div class="form-group">
             <label>监测时间</label>
             <input type="datetime-local" v-model="dataForm.time" required>
          </div>
          <div class="form-group">
             <label>测量类型 (可选)</label>
             <input v-model="dataForm.measurement_type" placeholder="如：左右岸, 上下游...">
          </div>
          <div class="modal-actions">
            <button type="button" @click="showDataModal = false">取消</button>
            <button type="submit" class="btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import * as echarts from 'echarts'

const router = useRouter()
const currentTab = ref('users')
const users = ref([])
const points = ref([])
const showPointModal = ref(false)
const isEditing = ref(false)
const showUserModal = ref(false)
const isEditingUser = ref(false)
const pointTypeFilter = ref('')

// 根据类型筛选测点
const filteredPoints = computed(() => {
  if (!pointTypeFilter.value) {
    return points.value
  }
  return points.value.filter(p => p.device_type === pointTypeFilter.value)
})

// 数据中心：根据选择的类型筛选可选测点
const filteredPointsForData = computed(() => {
    if (!dataFilters.type) {
        return points.value
    }
    return points.value.filter(p => p.device_type === dataFilters.type)
})

const pointForm = reactive({
  point_code: '',
  point_name: '',
  device_type: '倒垂线',
  longitude: 0,
  latitude: 0,
  height: 0
})

const userForm = reactive({
    id: null,
    username: '',
    password: '',
    email: '',
    role: 'user'
})

/* Data Center Vars */
const measurements = ref([])
const chartData = ref([])  // 图表专用数据
const showDataModal = ref(false)
const isDataEditing = ref(false)
const viewMode = ref('table')
const chartDiv = ref(null)
const chartInstance = ref(null)
const currentPage = ref(1)
const pageSize = 50
const totalCount = ref(0)

const dataFilters = reactive({
    startTime: '',
    endTime: '',
    type: '',
    name: ''
})

const dataForm = reactive({
    id: null,
    point_code: '',
    value: 0,
    time: '',
    measurement_type: ''
})

/* Data Center Functions */
const switchView = (mode) => {
    viewMode.value = mode
    if (mode === 'chart') {
        nextTick(initChart)
    }
}

const formatDate = (str) => {
    if(!str) return ''
    return str.replace('T', ' ')
}

const fetchData = async (resetPage = true) => {
    try {
        if (resetPage) currentPage.value = 1
        
        const params = {
            skip: (currentPage.value - 1) * pageSize,
            limit: pageSize
        }
        if (dataFilters.startTime) params.start_time = new Date(dataFilters.startTime).toISOString()
        if (dataFilters.endTime) params.end_time = new Date(dataFilters.endTime).toISOString()
        if (dataFilters.type) params.device_type = dataFilters.type
        if (dataFilters.name) params.point_name = dataFilters.name
        
        console.log('Fetching data with params:', params)
        const res = await api.get('/measurements/search', { params })
        console.log('API response:', res.data)
        measurements.value = res.data
        
        // 获取总数（简单估算：如果返回满页则可能有更多）
        if (currentPage.value === 1) {
            // 获取一次大量数据来统计总数
            const countParams = { ...params, skip: 0, limit: 10000 }
            const countRes = await api.get('/measurements/search', { params: countParams })
            totalCount.value = countRes.data.length
            chartData.value = countRes.data  // 用于图表
            console.log('Total count:', totalCount.value)
        }
        
        if (viewMode.value === 'chart') {
            nextTick(initChart)
        }
    } catch (e) {
        console.error('Fetch error:', e)
        alert('查询数据失败: ' + (e.response?.data?.detail || e.message || '未知错误'))
    }
}

const changePage = (delta) => {
    currentPage.value += delta
    fetchData(false)
}

const initChart = () => {
    if (!chartDiv.value) return
    
    if (chartInstance.value) {
        chartInstance.value.dispose()
    }
    chartInstance.value = echarts.init(chartDiv.value)
    
    // 使用 chartData（包含更多数据用于绘图）
    let dataToPlot = chartData.value
    
    // 如果没有选择时间范围且数据量很大，只显示最近一部分数据
    if (!dataFilters.startTime && !dataFilters.endTime && dataToPlot.length > 500) {
        // 按时间排序后取最近500条
        dataToPlot = [...dataToPlot].sort((a, b) => new Date(b.time) - new Date(a.time)).slice(0, 500)
    }
    
    // Group by point
    const grouped = {}
    dataToPlot.forEach(m => {
        const name = m.point_name || m.point_code
        if (!grouped[name]) grouped[name] = []
        grouped[name].push([m.time, m.value])
    })
    
    // Series
    const series = Object.keys(grouped).map(name => ({
        name,
        type: 'line',
        showSymbol: dataToPlot.length < 200,
        data: grouped[name].sort((a,b) => new Date(a[0]) - new Date(b[0]))
    }))
    
    const option = {
        title: { text: '监测数据趋势' },
        tooltip: { trigger: 'axis' },
        legend: { data: Object.keys(grouped), type: 'scroll' },
        xAxis: { type: 'time' },
        yAxis: { type: 'value', scale: true }, // scale: true 让Y轴不从0开始
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        dataZoom: [
            { type: 'slider', show: true },
            { type: 'inside' }
        ],
        series
    }
    chartInstance.value.setOption(option)
}

const openDataModal = (data) => {
    isDataEditing.value = !!data
    if (data) {
        Object.assign(dataForm, {
            id: data.id,
            point_code: data.point_code,
            value: data.value,
            time: data.time ? data.time.slice(0, 16) : '',
            measurement_type: data.measurement_type
        })
    } else {
        Object.assign(dataForm, {
            id: null,
            point_code: points.value.length > 0 ? points.value[0].point_code : '',
            value: 0,
            time: new Date().toISOString().slice(0, 16),
            measurement_type: ''
        })
    }
    showDataModal.value = true
}

const saveData = async () => {
    try {
        const payload = { ...dataForm }
        if (payload.time) payload.time = new Date(payload.time).toISOString()
        
        if (isDataEditing.value) {
            await api.put(`/measurements/${payload.id}`, payload)
        } else {
            await api.post('/measurements/', payload)
        }
        showDataModal.value = false
        fetchData()
    } catch (e) {
        console.error(e)
        alert('保存失败: ' + (e.response?.data?.detail || e.message))
    }
}

const deleteData = async (id) => {
    if(!confirm('确定删除这条数据吗？')) return
    try {
        await api.delete(`/measurements/${id}`)
        fetchData()
    } catch (e) {
        console.error(e)
        alert('删除失败')
    }
}

const goBack = () => router.push('/')

const fetchUsers = async () => {
  try {
    const res = await api.get('/auth/users')
    users.value = res.data
  } catch (e) {
    console.error(e)
    alert('获取用户列表失败')
  }
}

const openUserModal = (user) => {
    isEditingUser.value = !!user
    if (user) {
        Object.assign(userForm, {
            id: user.id,
            username: user.username,
            email: user.email,
            role: user.role,
            password: ''
        })
    } else {
        Object.assign(userForm, {
            id: null,
            username: '',
            email: '',
            role: 'user',
            password: ''
        })
    }
    showUserModal.value = true
}

const saveUser = async () => {
    try {
        if (isEditingUser.value) {
            const updateData = {
                email: userForm.email,
                role: userForm.role
            }
            if (userForm.password) {
                updateData.password = userForm.password
            }
            await api.put(`/auth/users/${userForm.id}`, updateData)
        } else {
            await api.post('/auth/users', userForm)
        }
        showUserModal.value = false
        fetchUsers()
    } catch (e) {
        console.error(e)
        alert('保存失败: ' + (e.response?.data?.detail || e.message))
    }
}

const deleteUser = async (id) => {
    if(!confirm('确定删除该用户吗？')) return
    try {
        await api.delete(`/auth/users/${id}`)
        fetchUsers()
    } catch (e) {
        console.error(e)
        alert('删除失败')
    }
}

const fetchPoints = async () => {
  try {
    const res = await api.get('/points/')
    points.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const deletePoint = async (code) => {
  if(!confirm('确定删除该测点吗？')) return
  try {
    await api.delete(`/points/${code}`)
    fetchPoints()
  } catch (e) {
    console.error(e)
    alert('删除失败')
  }
}

const openPointModal = (point) => {
  if (point) {
    isEditing.value = true
    Object.assign(pointForm, point)
  } else {
    isEditing.value = false
    Object.assign(pointForm, {
      point_code: '',
      point_name: '',
      device_type: '倒垂线',
      longitude: 0,
      latitude: 0,
      height: 0
    })
  }
  showPointModal.value = true
}

const savePoint = async () => {
  try {
    if (isEditing.value) {
      await api.put(`/points/${pointForm.point_code}`, pointForm)
    } else {
      await api.post('/points/', pointForm)
    }
    showPointModal.value = false
    fetchPoints()
  } catch (e) {
    console.error(e)
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

onMounted(() => {
  fetchUsers()
  fetchPoints()
})
</script>

<style scoped>
.admin-container {
  display: flex;
  height: 100vh;
  background-color: #f0f2f5;
  color: #333;
}

.admin-sidebar {
  width: 250px;
  background: #001529;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.sidebar-title {
  height: 64px;
  line-height: 64px;
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  background: #002140;
}

.menu-item {
  padding: 15px 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.menu-item:hover {
  background: #1890ff;
}

.menu-item.active {
  background: #1890ff;
}

.back-btn {
  margin-top: auto;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.admin-content {
  flex: 1;
  padding: 24px;
  overflow: auto;
}

.panel {
  background: #fff;
  padding: 24px;
  border-radius: 8px; /* 圆角 - 需求 3 */
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  color: #666;
  font-size: 14px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  min-width: 120px;
  cursor: pointer;
}

.filter-select:focus {
  border-color: #1890ff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th, .admin-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.tag-admin {
  background: #f50;
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.tag-user {
  background: #87d068;
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.btn-primary {
  background: #1890ff;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-danger {
  background: #ff4d4f;
  color: #fff;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 8px;
}

.btn-edit {
  background: #52c41a;
  color: #fff;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  width: 500px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}

.view-mode-toggle {
    display: flex;
    gap: 0;
    border: 1px solid #1890ff;
    border-radius: 4px;
    overflow: hidden;
    margin-left: 16px;
}
.toggle-btn {
    padding: 6px 16px;
    border: none;
    background: #fff;
    cursor: pointer;
    color: #1890ff;
}
.toggle-btn.active {
    background: #1890ff;
    color: #fff;
}
.filter-input {
    padding: 8px;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    /* width: 140px; */
}
.chart-wrapper {
    margin-top: 20px;
    background: #fff;
    padding: 10px;
    border: 1px solid #f0f0f0;
}
</style>