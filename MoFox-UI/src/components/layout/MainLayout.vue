<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const menuItems = [
  { name: 'DASHBOARD', icon: 'grid_view', path: '/' },
  { name: 'LOGS', icon: 'article', path: '/logs' },
  { name: 'USERS', icon: 'group', path: '/users' },
  { name: 'TRAINING', icon: 'model_training', path: '/training' },
  { name: 'SETTINGS', icon: 'settings', path: '/settings' },
]

const activeItem = ref('/')
</script>

<template>
  <div class="layout-container">
    <aside class="sidebar">
      <div class="brand">
        <div class="logo-box">AI</div>
        <span class="brand-text">NEXUS<span class="light">UI</span></span>
      </div>
      
      <nav>
        <div 
          v-for="item in menuItems" 
          :key="item.path"
          class="nav-item"
          :class="{ active: activeItem === item.path }"
          @click="activeItem = item.path"
        >
          <span class="material-icons">{{ item.icon }}</span> <!-- Placeholder for icons -->
          {{ item.name }}
        </div>
      </nav>
      
      <div class="system-health">
        <div class="label">SYSTEM HEALTH</div>
        <div class="status"><span class="dot"></span> ONLINE 99%</div>
      </div>
    </aside>
    
    <main class="main-content">
      <header class="top-bar">
        <div class="breadcrumbs"> / HOME / DASHBOARD / OVERVIEW </div>
        <div class="user-profile">
          <div class="avatar"></div>
        </div>
      </header>
      
      <div class="content-area">
        <router-view></router-view>
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
.layout-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 260px;
  background: var(--color-bg-card);
  border-right: var(--border-width) solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: 20px;
  
  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 40px;
    
    .logo-box {
      background: black;
      color: white;
      padding: 5px 8px;
      font-weight: bold;
    }
    
    .brand-text {
      font-weight: bold;
      font-size: 1.2rem;
      .light { font-weight: normal; }
    }
  }
  
  .nav-item {
    padding: 15px;
    margin-bottom: 5px;
    cursor: pointer;
    font-weight: bold;
    display: flex;
    align-items: center;
    gap: 10px;
    border: 2px solid transparent;
    
    &:hover {
      background: #f0f0f0;
    }
    
    &.active {
      background: black;
      color: white;
      border: 2px solid black;
    }
  }
  
  .system-health {
    margin-top: auto;
    border: 2px solid #eee;
    padding: 15px;
    
    .label { font-size: 0.7rem; color: #888; margin-bottom: 5px; }
    .status { 
      font-weight: bold; 
      display: flex; 
      align-items: center; 
      gap: 5px;
      
      .dot {
        width: 10px;
        height: 10px;
        background: var(--color-accent-green);
        display: inline-block;
      }
    }
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-app);
  
  .top-bar {
    height: 60px;
    border-bottom: var(--border-width) solid #eee;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 30px;
    background: white;
    
    .breadcrumbs {
      color: #888;
      font-size: 0.8rem;
      font-weight: bold;
    }
    
    .avatar {
      width: 35px;
      height: 35px;
      background: #ddd;
      border: 2px solid black;
    }
  }
  
  .content-area {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
  }
}
</style>
