<template>
  <div class="dashboard-home">
    <StatsCards />
    <MainContent />
    <BottomGrid />
  </div>
</template>

<script setup lang="ts">
import StatsCards from '@/components/StatsCards.vue'
import MainContent from '@/components/MainContent.vue'
import BottomGrid from '@/components/BottomGrid.vue'
</script>

<style scoped>
.dashboard-home {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
