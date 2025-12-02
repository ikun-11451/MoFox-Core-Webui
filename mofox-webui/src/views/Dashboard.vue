<template>
  <div class="dashboard-wrapper">
    <Sidebar />
    <div class="main-layout">
      <DashboardHeader />
      <div class="dashboard-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from '@/components/Sidebar.vue'
import DashboardHeader from '@/components/DashboardHeader.vue'
</script>

<style scoped>
.dashboard-wrapper {
  min-height: 100vh;
  background-color: var(--bg-light);
  display: flex;
}

.main-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  width: 100%;
  flex: 1;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
