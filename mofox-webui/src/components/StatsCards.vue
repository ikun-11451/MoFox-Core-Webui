<template>
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-title">总请求数</span>
        <Icon icon="material-symbols:bar-chart" class="stat-icon" />
      </div>
      <div class="stat-value">{{ stats.totalRequests }}</div>
      <div class="stat-description">API调用次数</div>
    </div>
    
    <div class="stat-card success">
      <div class="stat-header">
        <span class="stat-title">在线时长</span>
        <Icon icon="material-symbols:timer-outline" class="stat-icon" />
      </div>
      <div class="stat-value">{{ stats.onlineTime }}</div>
      <div class="stat-description">本次运行时间</div>
    </div>
    
    <div class="stat-card warning">
      <div class="stat-header">
        <span class="stat-title">Token消耗</span>
        <Icon icon="material-symbols:token-outline" class="stat-icon" />
      </div>
      <div class="stat-value">{{ stats.totalTokens }}</div>
      <div class="stat-description">输入+输出Token总数</div>
    </div>
    
    <div class="stat-card danger">
      <div class="stat-header">
        <span class="stat-title">API成本</span>
        <Icon icon="material-symbols:attach-money" class="stat-icon" />
      </div>
      <div class="stat-value">¥{{ stats.totalCost }}</div>
      <div class="stat-description">本次运行总花费</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'

const stats = ref({
  totalRequests: 17,
  onlineTime: '28分钟',
  totalTokens: '2,287',
  totalCost: '0.023'
})

onMounted(() => {
  // TODO: 从API获取实时数据
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: var(--bg-white);
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.1);
  border-left: 4px solid var(--primary-blue);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.15);
}

.stat-card.success {
  border-left-color: var(--success-green);
}

.stat-card.warning {
  border-left-color: var(--warning-yellow);
}

.stat-card.danger {
  border-left-color: var(--danger-red);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.stat-title {
  font-size: 9px;
  color: var(--text-gray);
}

.stat-icon {
  font-size: 20px;
}

.stat-value {
  font-size: 24px;
  color: var(--primary-blue);
  margin-bottom: 8px;
}

.stat-description {
  font-size: 7px;
  color: var(--text-gray);
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
