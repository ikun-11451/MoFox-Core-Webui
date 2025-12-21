<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { startUpdateChecker, stopUpdateChecker, setToastCallback } from '@/utils/updateChecker'
import { setupToast, useToast } from '@/composables/useToast'

// 初始化主题
useThemeStore()

// 初始化 Toast 系统
setupToast()
const toast = useToast()

// Toast 显示函数
function showToast(message: string, type: 'success' | 'error') {
  if (type === 'success') {
    toast.success(message)
  } else {
    toast.error(message)
  }
}

// 启动时设置 Toast 回调并启动更新检查器
onMounted(() => {
  setToastCallback(showToast)
  startUpdateChecker()
})

// 卸载时停止更新检查器
onUnmounted(() => {
  stopUpdateChecker()
})
</script>

