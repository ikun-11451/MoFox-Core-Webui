<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo-icon">🦊</div>
      <h1 class="sidebar-title" v-if="!collapsed">MoFox</h1>
    </div>
    
    <nav class="sidebar-nav">
      <router-link to="/dashboard" class="nav-item" active-class="active" exact-active-class="active">
        <Icon icon="material-symbols:dashboard-outline" class="nav-icon" />
        <span v-if="!collapsed">仪表盘</span>
      </router-link>
      <a href="#" class="nav-item">
        <Icon icon="material-symbols:chat-bubble-outline" class="nav-icon" />
        <span v-if="!collapsed">聊天记录</span>
      </a>
      <a href="#" class="nav-item">
        <Icon icon="material-symbols:analytics-outline" class="nav-icon" />
        <span v-if="!collapsed">统计分析</span>
      </a>
      <router-link to="/dashboard/settings" class="nav-item" active-class="active">
        <Icon icon="material-symbols:settings-outline" class="nav-icon" />
        <span v-if="!collapsed">系统设置</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <button class="collapse-btn" @click="toggleCollapse">
        <Icon :icon="collapsed ? 'material-symbols:chevron-right' : 'material-symbols:chevron-left'" />
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'

const collapsed = ref(false)

const toggleCollapse = () => {
  collapsed.value = !collapsed.value
}
</script>

<style scoped>
.sidebar {
  height: 100vh;
  background: var(--bg-white);
  border-right: 2px solid var(--lighter-blue);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  width: v-bind('collapsed ? "64px" : "240px"');
  position: sticky;
  top: 0;
  z-index: 100;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 2px solid var(--lighter-blue);
  padding: 0 10px;
}

.logo-icon {
  font-size: 24px;
  margin-right: v-bind('collapsed ? "0" : "10px"');
}

.sidebar-title {
  font-size: 14px;
  color: var(--primary-blue);
  font-family: 'Press Start 2P', cursive;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  color: var(--text-dark);
  text-decoration: none;
  transition: all 0.2s;
  font-size: 10px;
  white-space: nowrap;
  overflow: hidden;
}

.nav-item:hover {
  background-color: var(--bg-light);
  color: var(--primary-blue);
}

.nav-item.active {
  background-color: rgba(74, 144, 226, 0.1);
  color: var(--primary-blue);
  border-right: 3px solid var(--primary-blue);
}

.nav-icon {
  font-size: 20px;
  margin-right: v-bind('collapsed ? "0" : "12px"');
  min-width: 20px;
}

.sidebar-footer {
  padding: 10px;
  border-top: 2px solid var(--lighter-blue);
  display: flex;
  justify-content: flex-end;
}

.collapse-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-gray);
  padding: 5px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-btn:hover {
  background-color: var(--bg-light);
  color: var(--primary-blue);
}
</style>
