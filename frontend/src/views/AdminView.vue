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
      <div class="menu-item back-btn" @click="goBack">
        &lt; 返回地图
      </div>
    </div>
    
    <div class="admin-content">
      <!-- 用户管理面板 -->
      <div v-if="currentTab === 'users'" class="panel">
        <div class="panel-header">
          <h2>用户管理</h2>
          <!-- 暂时不支持前端注册新管理员，只能查看和删除，或者简单的添加 -->
          <!-- <button class="btn-primary" @click="showAddUserAPI">添加用户</button> -->
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
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

const router = useRouter()
const currentTab = ref('users')
const users = ref([])
const points = ref([])
const showPointModal = ref(false)
const isEditing = ref(false)
const pointTypeFilter = ref('')

// 根据类型筛选测点
const filteredPoints = computed(() => {
  if (!pointTypeFilter.value) {
    return points.value
  }
  return points.value.filter(p => p.device_type === pointTypeFilter.value)
})

const pointForm = reactive({
  point_code: '',
  point_name: '',
  device_type: '倒垂线',
  longitude: 0,
  latitude: 0,
  height: 0
})

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

const fetchPoints = async () => {
  try {
    const res = await api.get('/points/')
    points.value = res.data
  } catch (e) {
    console.error(e)
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
</style>