<template>
  <header class="dashboard-header">
    <div class="header-container">
      <div class="page-title">
        仪表盘
      </div>
      <div class="user-info">
        <span class="status-badge">● 运行中</span>
        <button class="pixel-button theme-toggle" @click="themeStore.toggleTheme">
          {{ themeStore.theme === 'light' ? '🌙' : '☀️' }}
        </button>
        <button class="pixel-button" @click="handleLogout">登出</button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard-header {
  background: var(--bg-white);
  box-shadow: 0 2px 8px var(--shadow);
  margin-bottom: 30px;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 16px;
  color: var(--text-dark);
  font-weight: bold;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 8px;
  background: var(--success-green);
  color: white;
}

.pixel-button {
  padding: 10px 20px;
  background: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 4px;
  font-family: 'Press Start 2P', sans-serif;
  font-size: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.pixel-button:hover {
  background: var(--light-blue);
  transform: scale(1.05);
}

.pixel-button:active {
  transform: scale(0.95);
}
</style>
