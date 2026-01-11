<template>
  <div class="login-container">
    <!-- 背景动态粒子效果 -->
    <div class="bg-particles">
      <div class="particle" v-for="n in 50" :key="n"></div>
    </div>
    
    <div class="login-wrapper">
      <div class="login-card">
        <!-- Logo 区域 -->
        <div class="logo-section">
          <div class="logo-icon">🏛️</div>
          <h1 class="login-title">重力坝三维数据中心</h1>
          <p class="login-subtitle">Gravity Dam 3D Data Center</p>
        </div>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <div class="input-wrapper">
              <span class="input-icon">👤</span>
              <input 
                type="text" 
                id="username" 
                v-model="username" 
                placeholder="请输入用户名" 
                required 
                class="form-input"
              />
            </div>
          </div>
          
          <div class="form-group">
            <div class="input-wrapper">
              <span class="input-icon">🔒</span>
              <input 
                type="password" 
                id="password" 
                v-model="password" 
                placeholder="请输入密码" 
                required 
                class="form-input"
              />
            </div>
          </div>

          <div v-if="error" class="error-message">
            <span class="error-icon">⚠️</span>
            {{ error }}
          </div>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? '登录中...' : '登 录' }}
          </button>
        </form>
        
        <div class="login-footer">
          <p>© 2026 重力坝安全监测系统</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '@/utils/api';

const router = useRouter();
const username = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    await login(username.value, password.value);
    router.push('/'); // 登录成功跳转到主页
  } catch (err) {
    console.error('Login failed:', err);
    if (err.response && err.response.data && err.response.data.detail) {
        error.value = err.response.data.detail;
    } else {
        error.value = '登录失败，请检查网络或联系管理员';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 50%, #0d2137 100%);
  position: relative;
  overflow: hidden;
}

/* 背景粒子动画 */
.bg-particles {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(0, 229, 255, 0.6);
  border-radius: 50%;
  animation: float 15s infinite;
}

.particle:nth-child(odd) {
  background: rgba(0, 160, 233, 0.4);
  width: 3px;
  height: 3px;
}

@keyframes float {
  0%, 100% {
    transform: translateY(100vh) translateX(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) translateX(100px);
    opacity: 0;
  }
}

/* 随机分布粒子 */
.particle:nth-child(1) { left: 5%; animation-delay: 0s; animation-duration: 12s; }
.particle:nth-child(2) { left: 10%; animation-delay: 1s; animation-duration: 14s; }
.particle:nth-child(3) { left: 15%; animation-delay: 2s; animation-duration: 11s; }
.particle:nth-child(4) { left: 20%; animation-delay: 0.5s; animation-duration: 16s; }
.particle:nth-child(5) { left: 25%; animation-delay: 3s; animation-duration: 13s; }
.particle:nth-child(6) { left: 30%; animation-delay: 1.5s; animation-duration: 15s; }
.particle:nth-child(7) { left: 35%; animation-delay: 2.5s; animation-duration: 12s; }
.particle:nth-child(8) { left: 40%; animation-delay: 0.8s; animation-duration: 14s; }
.particle:nth-child(9) { left: 45%; animation-delay: 3.5s; animation-duration: 11s; }
.particle:nth-child(10) { left: 50%; animation-delay: 1.2s; animation-duration: 16s; }
.particle:nth-child(11) { left: 55%; animation-delay: 2.8s; animation-duration: 13s; }
.particle:nth-child(12) { left: 60%; animation-delay: 0.3s; animation-duration: 15s; }
.particle:nth-child(13) { left: 65%; animation-delay: 1.8s; animation-duration: 12s; }
.particle:nth-child(14) { left: 70%; animation-delay: 3.2s; animation-duration: 14s; }
.particle:nth-child(15) { left: 75%; animation-delay: 0.6s; animation-duration: 11s; }
.particle:nth-child(16) { left: 80%; animation-delay: 2.2s; animation-duration: 16s; }
.particle:nth-child(17) { left: 85%; animation-delay: 1.4s; animation-duration: 13s; }
.particle:nth-child(18) { left: 90%; animation-delay: 3.8s; animation-duration: 15s; }
.particle:nth-child(19) { left: 95%; animation-delay: 0.9s; animation-duration: 12s; }
.particle:nth-child(20) { left: 3%; animation-delay: 2.6s; animation-duration: 14s; }

.login-wrapper {
  z-index: 10;
}

.login-card {
  background: rgba(10, 25, 50, 0.85);
  padding: 50px 40px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(0, 160, 233, 0.15);
  width: 100%;
  max-width: 420px;
  text-align: center;
  border: 1px solid rgba(0, 160, 233, 0.3);
  backdrop-filter: blur(10px);
}

.logo-section {
  margin-bottom: 35px;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.login-title {
  margin: 0;
  color: #00e5ff;
  font-size: 28px;
  font-weight: bold;
  letter-spacing: 2px;
}

.login-subtitle {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  margin-top: 8px;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.login-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 20px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 15px;
  font-size: 16px;
  z-index: 1;
}

.form-input {
  width: 100%;
  padding: 14px 14px 14px 45px;
  border: 1px solid rgba(0, 160, 233, 0.3);
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.form-input:focus {
  border-color: #00e5ff;
  outline: none;
  box-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
  background: rgba(255, 255, 255, 0.08);
}

.error-message {
  color: #ff6b6b;
  margin-bottom: 15px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  background: rgba(255, 77, 79, 0.1);
  padding: 10px;
  border-radius: 6px;
  border: 1px solid rgba(255, 77, 79, 0.3);
}

.error-icon {
  font-size: 14px;
}

.submit-btn {
  background: linear-gradient(135deg, #00a0e9 0%, #00e5ff 100%);
  color: white;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  letter-spacing: 4px;
  box-shadow: 0 4px 15px rgba(0, 160, 233, 0.4);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(0, 229, 255, 0.5);
}

.submit-btn:active {
  transform: translateY(0);
}

.submit-btn:disabled {
  background: linear-gradient(135deg, #4a5568 0%, #718096 100%);
  cursor: not-allowed;
  box-shadow: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.login-footer p {
  color: rgba(255, 255, 255, 0.3);
  font-size: 12px;
  margin: 0;
}
</style>
