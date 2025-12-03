<template>
  <div class="login-wrapper">
    <!-- 像素风背景 -->
    <div class="pixel-bg">
      <div v-for="i in 9" :key="i" class="pixel-box" 
           :style="{ left: `${i * 10}%`, animationDelay: `${i * 2}s` }"></div>
    </div>
    
    <!-- 登录容器 -->
    <div class="login-container">
      <!-- Logo区域 -->
      <div class="logo-section">
        <Icon icon="material-symbols:smart-toy-outline" class="logo-icon" />
        <h1 class="logo-title">MoFox-Bot</h1>
        <p class="logo-subtitle">管理控制台登录</p>
      </div>
      
      <!-- 登录表单 -->
      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">密码</label>
          <input 
            v-model="loginForm.password"
            type="password" 
            class="form-input" 
            placeholder="请输入密码"
            required
          >
        </div>
        
        <div class="remember-section">
          <label class="checkbox-container">
            <input v-model="loginForm.remember" type="checkbox">
            <span>记住我</span>
          </label>
        </div>
        
        <button type="submit" class="login-button" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Icon } from '@iconify/vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const loginForm = reactive({
  password: '',
  remember: false
})

const handleLogin = async () => {
  loading.value = true
  
  // 模拟登录请求延迟
  setTimeout(() => {
    const success = userStore.login()
    loading.value = false
    
    if (success) {
      router.push('/dashboard')
    }
  }, 1000)
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 像素风背景动画 */
.pixel-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 0;
}

.pixel-box {
  position: absolute;
  width: 20px;
  height: 20px;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0;
  }
  10%, 90% {
    opacity: 1;
  }
  50% {
    transform: translateY(-100vh) rotate(360deg);
  }
}

/* 登录容器 */
.login-container {
  background: var(--bg-white);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 450px;
  padding: 50px 40px;
  position: relative;
  z-index: 1;
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Logo区域 */
.logo-section {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  font-size: 64px;
  margin-bottom: 20px;
  display: inline-block;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.logo-title {
  font-size: 18px;
  color: var(--primary-blue);
  margin-bottom: 8px;
}

.logo-subtitle {
  font-size: 8px;
  color: var(--text-gray);
}

/* 表单样式 */
.login-form {
  margin-bottom: 25px;
}

.form-group {
  margin-bottom: 25px;
}

.form-label {
  display: block;
  font-size: 9px;
  color: var(--text-dark);
  margin-bottom: 10px;
}

.form-input {
  width: 100%;
  padding: 15px;
  border: 2px solid var(--lighter-blue);
  border-radius: 8px;
  font-family: 'Press Start 2P', sans-serif;
  font-size: 10px;
  background: var(--bg-white);
  color: var(--text-dark);
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px var(--shadow);
}

.form-input::placeholder {
  color: var(--text-gray);
  opacity: 0.6;
}

/* 记住我复选框 */
.remember-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 25px;
  font-size: 8px;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.checkbox-container input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--primary-blue);
}

.forgot-link {
  color: var(--primary-blue);
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-link:hover {
  color: var(--light-blue);
}

/* 按钮样式 */
.login-button {
  width: 100%;
  padding: 15px;
  background: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 8px;
  font-family: 'Press Start 2P', sans-serif;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.login-button:hover:not(:disabled) {
  background: var(--light-blue);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px var(--shadow);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 分割线 */
.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 30px 0;
  color: var(--text-gray);
  font-size: 8px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--lighter-blue);
}

.divider span {
  padding: 0 15px;
}

/* 社交登录 */
.social-login {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.social-button {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  border: 2px solid var(--lighter-blue);
  background: var(--bg-white);
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.social-button:hover {
  border-color: var(--primary-blue);
  transform: scale(1.1);
}

/* 注册提示 */
.register-prompt {
  text-align: center;
  font-size: 8px;
  color: var(--text-gray);
  margin-top: 25px;
}

.register-link {
  color: var(--primary-blue);
  text-decoration: none;
  font-weight: bold;
}

.register-link:hover {
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-container {
    padding: 40px 30px;
  }
  
  .logo-icon {
    font-size: 48px;
  }
  
  .logo-title {
    font-size: 14px;
  }
}
</style>
