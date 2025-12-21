<template>
  <button
    class="btn"
    :class="[variant, size, { loading, disabled, 'icon-only': iconOnly }]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <Icon v-if="loading" icon="lucide:loader-2" class="spinning" />
    <Icon v-else-if="icon" :icon="icon" />
    <span v-if="!iconOnly">
      <slot></slot>
    </span>
  </button>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'icon'
  size?: 'small' | 'medium' | 'large'
  icon?: string
  iconOnly?: boolean
  loading?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'medium',
  iconOnly: false,
  loading: false,
  disabled: false
})

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

function handleClick(event: MouseEvent) {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  position: relative;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.loading {
  pointer-events: none;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Variants */
.btn.primary {
  background: #3b82f6;
  color: white;
}

.btn.primary:hover:not(:disabled):not(.loading) {
  background: #2563eb;
}

.btn.secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn.secondary:hover:not(:disabled):not(.loading) {
  background: #e5e7eb;
}

.btn.danger {
  background: #ef4444;
  color: white;
}

.btn.danger:hover:not(:disabled):not(.loading) {
  background: #dc2626;
}

.btn.ghost {
  background: transparent;
  color: #6b7280;
}

.btn.ghost:hover:not(:disabled):not(.loading) {
  background: #f3f4f6;
  color: #111827;
}

.btn.icon {
  background: transparent;
  color: #6b7280;
  padding: 6px;
  border-radius: 6px;
}

.btn.icon:hover:not(:disabled):not(.loading) {
  background: #f3f4f6;
  color: #111827;
}

/* Sizes */
.btn.small {
  padding: 6px 12px;
  font-size: 13px;
}

.btn.small.icon-only {
  padding: 6px;
}

.btn.medium {
  padding: 8px 16px;
  font-size: 14px;
}

.btn.medium.icon-only {
  padding: 8px;
}

.btn.large {
  padding: 10px 20px;
  font-size: 15px;
}

.btn.large.icon-only {
  padding: 10px;
}

.icon-only span {
  display: none;
}
</style>
