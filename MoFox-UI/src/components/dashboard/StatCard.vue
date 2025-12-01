<script setup lang="ts">
defineProps<{
  title: string
  value: string
  subtext: string
  icon?: string
  trend?: string
}>()
</script>

<template>
  <div class="retro-card stat-card">
    <div class="card-header">
      <span class="title">{{ title }}</span>
      <span class="icon" v-if="icon">{{ icon }}</span>
    </div>
    <div class="value">{{ value }}</div>
    <div class="subtext" :class="{ positive: trend === 'up' }">
      {{ subtext }}
    </div>
  </div>
</template>

<style scoped lang="scss">
.stat-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 140px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    
    .title {
      font-size: 0.8rem;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
  }
  
  .value {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 5px;
  }
  
  .subtext {
    font-size: 0.8rem;
    color: #666;
    
    &.positive {
      color: var(--color-accent-green);
    }
  }
}
</style>
