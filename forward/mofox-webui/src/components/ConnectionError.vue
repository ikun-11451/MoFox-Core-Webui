<template>
  <Modal 
    v-model="isVisible"
    title="连接失败"
    icon="lucide:wifi-off"
    width="320px"
    :show-footer="false"
    :close-on-click-outside="false"
    @close="handleClose"
  >
    <div class="connection-error-content">
      <p class="error-message">
        无法连接到后端服务器
      </p>
      <p class="error-detail">
        {{ message || '请检查服务是否正常运行' }}
      </p>
      <div class="error-actions">
        <Button variant="primary" icon="lucide:refresh-cw" @click="handleRetry">
          重试连接
        </Button>
        <Button variant="secondary" @click="handleClose">
          关闭
        </Button>
      </div>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Modal from '@/components/common/Modal.vue'
import Button from '@/components/common/Button.vue'

interface Props {
  visible: boolean
  message?: string
}

interface Emits {
  (e: 'close'): void
  (e: 'retry'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isVisible = computed({
  get: () => props.visible,
  set: (value) => {
    if (!value) {
      emit('close')
    }
  }
})

function handleClose() {
  emit('close')
}

function handleRetry() {
  emit('retry')
}
</script>

<style scoped>
.connection-error-content {
  text-align: center;
}

.error-message {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 8px;
}

.error-detail {
  font-size: 13px;
  color: #ef4444;
  margin: 0 0 24px;
}

.error-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>

.m3-button {
  height: 40px;
  border-radius: 20px;
  padding: 0 24px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  width: 100%;
}

.m3-button.filled {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

.m3-button.filled:hover {
  box-shadow: var(--md-sys-elevation-1);
  background: linear-gradient(rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.08)), var(--md-sys-color-primary);
}

.m3-button.text {
  background: transparent;
  color: var(--md-sys-color-primary);
}

.m3-button.text:hover {
  background: var(--md-sys-color-surface-container-highest);
}

/* 过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
  opacity: 0;
}
