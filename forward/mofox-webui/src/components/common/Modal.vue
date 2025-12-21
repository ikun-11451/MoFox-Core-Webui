<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="modelValue" class="m3-dialog-overlay" @click="handleOverlayClick">
        <div class="m3-dialog" :class="{ large: large }" :style="{ maxWidth: width }" @click.stop>
          <!-- 头部 -->
          <div class="dialog-header">
            <h3>
              <span v-if="icon" class="material-symbols-rounded">{{ icon }}</span>
              {{ title }}
            </h3>
            <button v-if="showClose" class="m3-icon-button" @click="handleClose">
              <span class="material-symbols-rounded">close</span>
            </button>
          </div>
          
          <!-- 内容 -->
          <div class="dialog-body">
            <slot></slot>
          </div>
          
          <!-- 底部 -->
          <div v-if="showFooter" class="dialog-actions">
            <slot name="footer">
              <button class="m3-button text" @click="handleCancel">
                {{ cancelText }}
              </button>
              <button 
                class="m3-button filled" 
                :disabled="confirmDisabled"
                @click="handleConfirm"
              >
                {{ confirmText }}
              </button>
            </slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean
  title?: string
  icon?: string
  width?: string
  large?: boolean
  showClose?: boolean
  showFooter?: boolean
  confirmText?: string
  cancelText?: string
  confirmDisabled?: boolean
  closeOnClickOutside?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '提示',
  width: '320px',
  large: false,
  showClose: true,
  showFooter: true,
  confirmText: '确定',
  cancelText: '取消',
  confirmDisabled: false,
  closeOnClickOutside: true
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
  (e: 'close'): void
}>()

function handleClose() {
  emit('update:modelValue', false)
  emit('close')
}

function handleConfirm() {
  emit('confirm')
}

function handleCancel() {
  emit('update:modelValue', false)
  emit('cancel')
}

function handleOverlayClick() {
  if (props.closeOnClickOutside) {
    handleClose()
  }
}
</script>

<style scoped>
/* MD3 Dialog Overlay */
.m3-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.32);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

/* MD3 Dialog Container */
.m3-dialog {
  background: var(--md-sys-color-surface-container-high);
  border-radius: 28px;
  padding: 24px;
  width: 90%;
  max-width: 320px;
  box-shadow: var(--md-sys-elevation-3);
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 80vh;
}

.m3-dialog.large {
  max-width: 500px;
}

/* Dialog Header */
.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dialog-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 20px;
  font-weight: 400;
  color: var(--md-sys-color-on-surface);
}

.dialog-header h3 .material-symbols-rounded {
  font-size: 24px;
}

.m3-icon-button {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: 20px;
  cursor: pointer;
  color: var(--md-sys-color-on-surface-variant);
  transition: all 0.2s;
}

.m3-icon-button:hover {
  background: var(--md-sys-color-surface-container-highest);
}

/* Dialog Body */
.dialog-body {
  overflow-y: auto;
  flex: 1;
  color: var(--md-sys-color-on-surface-variant);
}

/* Dialog Actions */
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* MD3 Button Styles */
.m3-button {
  height: 40px;
  padding: 0 24px;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  font-family: inherit;
}

.m3-button:disabled {
  opacity: 0.38;
  cursor: not-allowed;
}

.m3-button.filled {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

.m3-button.filled:hover:not(:disabled) {
  box-shadow: var(--md-sys-elevation-1);
}

.m3-button.text {
  background: transparent;
  color: var(--md-sys-color-primary);
}

.m3-button.text:hover:not(:disabled) {
  background: var(--md-sys-color-primary-container);
}

/* Dialog Transition */
.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.2s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}

.dialog-enter-active .m3-dialog,
.dialog-leave-active .m3-dialog {
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.dialog-enter-from .m3-dialog,
.dialog-leave-to .m3-dialog {
  transform: scale(0.9);
}
</style>
