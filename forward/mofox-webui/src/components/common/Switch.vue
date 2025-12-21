<template>
  <label 
    class="switch" 
    :class="[size, { disabled }]"
  >
    <input 
      type="checkbox" 
      :checked="modelValue"
      :disabled="disabled"
      @change="handleChange"
    />
    <span class="slider"></span>
  </label>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  disabled: false
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

function handleChange(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.checked)
}
</script>

<style scoped>
.switch {
  position: relative;
  display: inline-block;
  cursor: pointer;
}

.switch.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
  position: absolute;
}

.slider {
  position: relative;
  display: block;
  background-color: #d1d5db;
  transition: background-color 0.2s;
  border-radius: 999px;
}

.slider::before {
  content: '';
  position: absolute;
  background-color: white;
  transition: transform 0.2s;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.switch input:checked + .slider {
  background-color: #3b82f6;
}

.switch input:disabled + .slider {
  cursor: not-allowed;
}

/* Medium size (default) */
.switch.medium .slider {
  width: 44px;
  height: 24px;
}

.switch.medium .slider::before {
  width: 20px;
  height: 20px;
  left: 2px;
  top: 2px;
}

.switch.medium input:checked + .slider::before {
  transform: translateX(20px);
}

/* Small size */
.switch.small .slider {
  width: 36px;
  height: 20px;
}

.switch.small .slider::before {
  width: 16px;
  height: 16px;
  left: 2px;
  top: 2px;
}

.switch.small input:checked + .slider::before {
  transform: translateX(16px);
}

/* Large size */
.switch.large .slider {
  width: 52px;
  height: 28px;
}

.switch.large .slider::before {
  width: 24px;
  height: 24px;
  left: 2px;
  top: 2px;
}

.switch.large input:checked + .slider::before {
  transform: translateX(24px);
}
</style>
