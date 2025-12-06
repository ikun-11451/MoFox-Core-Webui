<template>
  <teleport to="body">
    <transition name="dialog-fade">
      <div v-if="visible" class="dialog-overlay" @click="handleOverlayClick">
        <div class="dialog-container" @click.stop>
          <div class="dialog-header">
            <div class="dialog-icon" :class="iconClass">
              <Icon :icon="iconName" />
            </div>
            <h3 class="dialog-title">{{ title }}</h3>
          </div>
          
          <div class="dialog-content">
            <p v-for="(line, index) in messageLines" :key="index" class="dialog-message">
              {{ line }}
            </p>
          </div>
          
          <div class="dialog-footer">
            <button 
              v-if="showCancel" 
              class="dialog-button cancel-button" 
              @click="handleCancel"
            >
              {{ cancelText }}
            </button>
            <button 
              class="dialog-button confirm-button" 
              :class="confirmButtonClass"
              @click="handleConfirm"
            >
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'

export interface ConfirmDialogProps {
  visible: boolean
  title?: string
  message: string
  type?: 'info' | 'success' | 'warning' | 'danger'
  showCancel?: boolean
  confirmText?: string
  cancelText?: string
}

const props = withDefaults(defineProps<ConfirmDialogProps>(), {
  title: '提示',
  type: 'info',
  showCancel: true,
  confirmText: '确定',
  cancelText: '取消'
})

const emit = defineEmits<{
  confirm: []
  cancel: []
  'update:visible': [value: boolean]
}>()

const messageLines = computed(() => {
  return props.message.split('\n').filter(line => line.trim())
})

const iconName = computed(() => {
  const icons = {
    info: 'lucide:info',
    success: 'lucide:check-circle',
    warning: 'lucide:alert-triangle',
    danger: 'lucide:alert-circle'
  }
  return icons[props.type]
})

const iconClass = computed(() => `icon-${props.type}`)

const confirmButtonClass = computed(() => {
  const classes = {
    info: 'primary',
    success: 'success',
    warning: 'warning',
    danger: 'danger'
  }
  return classes[props.type]
})

const handleConfirm = () => {
  emit('confirm')
  emit('update:visible', false)
}

const handleCancel = () => {
  emit('cancel')
  emit('update:visible', false)
}

const handleOverlayClick = () => {
  if (props.showCancel) {
    handleCancel()
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.dialog-container {
  background: var(--bg-primary);
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 420px;
  width: 100%;
  overflow: hidden;
  animation: dialog-bounce 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes dialog-bounce {
  0% {
    transform: scale(0.9);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.dialog-header {
  padding: 24px 24px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.dialog-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.icon-info {
  background: rgba(59, 130, 246, 0.1);
  color: var(--primary);
}

.icon-success {
  background: rgba(34, 197, 94, 0.1);
  color: var(--success);
}

.icon-warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning);
}

.icon-danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.dialog-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  text-align: center;
}

.dialog-content {
  padding: 0 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dialog-message {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
  text-align: center;
}

.dialog-footer {
  padding: 16px 24px 24px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.dialog-button {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 100px;
}

.cancel-button {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.cancel-button:hover {
  background: var(--bg-secondary);
  border-color: var(--text-tertiary);
}

.confirm-button {
  color: white;
}

.confirm-button.primary {
  background: var(--primary);
}

.confirm-button.primary:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.confirm-button.success {
  background: var(--success);
}

.confirm-button.success:hover {
  background: #16a34a;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
}

.confirm-button.warning {
  background: var(--warning);
}

.confirm-button.warning:hover {
  background: #d97706;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

.confirm-button.danger {
  background: var(--danger);
}

.confirm-button.danger:hover {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

/* 过渡动画 */
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.3s;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-fade-enter-active .dialog-container {
  animation: dialog-bounce 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.dialog-fade-leave-active .dialog-container {
  animation: dialog-bounce 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) reverse;
}

/* 响应式 */
@media (max-width: 768px) {
  .dialog-container {
    max-width: 90%;
  }
  
  .dialog-footer {
    flex-direction: column-reverse;
  }
  
  .dialog-button {
    width: 100%;
  }
}
</style>
