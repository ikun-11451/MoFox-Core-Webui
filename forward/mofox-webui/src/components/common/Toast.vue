<template>
  <Teleport to="body">
    <TransitionGroup name="toast" tag="div" class="toast-container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="[toast.type]"
        @click="removeToast(toast.id)"
      >
        <Icon :icon="getIcon(toast.type)" class="toast-icon" />
        <div class="toast-content">
          <div v-if="toast.title" class="toast-title">{{ toast.title }}</div>
          <div class="toast-message">{{ toast.message }}</div>
        </div>
        <button class="toast-close" @click.stop="removeToast(toast.id)">
          <Icon icon="lucide:x" />
        </button>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'

export interface Toast {
  id: number
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  title?: string
  duration?: number
}

const toasts = ref<Toast[]>([])
let nextId = 1

function getIcon(type: string) {
  const icons = {
    success: 'lucide:check-circle',
    error: 'lucide:x-circle',
    warning: 'lucide:alert-triangle',
    info: 'lucide:info'
  }
  return icons[type as keyof typeof icons] || icons.info
}

function addToast(toast: Omit<Toast, 'id'>) {
  const id = nextId++
  const newToast: Toast = {
    id,
    duration: 3000,
    ...toast
  }
  
  toasts.value.push(newToast)
  
  if (newToast.duration) {
    setTimeout(() => {
      removeToast(id)
    }, newToast.duration)
  }
  
  return id
}

function removeToast(id: number) {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

defineExpose({
  addToast,
  removeToast
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 300px;
  max-width: 500px;
  pointer-events: auto;
  cursor: pointer;
  transition: all 0.3s;
}

.toast:hover {
  transform: translateX(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.toast-icon {
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.toast.success {
  border-left: 4px solid #10b981;
}

.toast.success .toast-icon {
  color: #10b981;
}

.toast.error {
  border-left: 4px solid #ef4444;
}

.toast.error .toast-icon {
  color: #ef4444;
}

.toast.warning {
  border-left: 4px solid #f59e0b;
}

.toast.warning .toast-icon {
  color: #f59e0b;
}

.toast.info {
  border-left: 4px solid #3b82f6;
}

.toast.info .toast-icon {
  color: #3b82f6;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 14px;
  color: #111827;
  margin-bottom: 4px;
}

.toast-message {
  font-size: 14px;
  color: #6b7280;
  word-wrap: break-word;
}

.toast-close {
  padding: 4px;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: #9ca3af;
  flex-shrink: 0;
  transition: all 0.2s;
}

.toast-close:hover {
  background: #f3f4f6;
  color: #111827;
}

/* 过渡动画 */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.9);
}

.toast-move {
  transition: transform 0.3s;
}

@media (max-width: 640px) {
  .toast-container {
    left: 20px;
    right: 20px;
  }
  
  .toast {
    min-width: auto;
    width: 100%;
  }
}
</style>
