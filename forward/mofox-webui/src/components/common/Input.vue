<template>
  <div class="input-wrapper" :class="{ disabled, error: !!error, focused }">
    <div v-if="prefix || $slots.prefix" class="input-prefix">
      <slot name="prefix">
        <Icon v-if="prefix" :icon="prefix" />
      </slot>
    </div>
    
    <input
      v-if="type !== 'textarea'"
      :type="actualType"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      class="input"
      @input="handleInput"
      @focus="focused = true"
      @blur="focused = false"
    />
    
    <textarea
      v-else
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :rows="rows"
      class="input textarea"
      @input="handleInput"
      @focus="focused = true"
      @blur="focused = false"
    />
    
    <div v-if="suffix || $slots.suffix || (type === 'password' && showPasswordToggle)" class="input-suffix">
      <slot name="suffix">
        <button
          v-if="type === 'password' && showPasswordToggle"
          type="button"
          class="suffix-btn"
          @click="togglePassword"
        >
          <Icon :icon="passwordVisible ? 'lucide:eye-off' : 'lucide:eye'" />
        </button>
        <Icon v-else-if="suffix" :icon="suffix" />
      </slot>
    </div>
    
    <div v-if="clearable && modelValue" class="input-clear">
      <button type="button" class="suffix-btn" @click="handleClear">
        <Icon icon="lucide:x" />
      </button>
    </div>
  </div>
  
  <div v-if="error" class="input-error">{{ error }}</div>
  <div v-else-if="hint" class="input-hint">{{ hint }}</div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'

interface Props {
  modelValue: string | number
  type?: 'text' | 'password' | 'email' | 'number' | 'textarea'
  placeholder?: string
  prefix?: string
  suffix?: string
  disabled?: boolean
  readonly?: boolean
  clearable?: boolean
  showPasswordToggle?: boolean
  error?: string
  hint?: string
  rows?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  disabled: false,
  readonly: false,
  clearable: false,
  showPasswordToggle: true,
  rows: 3
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
}>()

const focused = ref(false)
const passwordVisible = ref(false)

const actualType = computed(() => {
  if (props.type === 'password' && passwordVisible.value) {
    return 'text'
  }
  return props.type
})

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement | HTMLTextAreaElement
  let value: string | number = target.value
  
  if (props.type === 'number') {
    value = target.value === '' ? '' : Number(target.value)
  }
  
  emit('update:modelValue', value)
}

function handleClear() {
  emit('update:modelValue', '')
}

function togglePassword() {
  passwordVisible.value = !passwordVisible.value
}
</script>

<style scoped>
.input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  transition: all 0.2s;
}

.input-wrapper.focused {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-wrapper.disabled {
  background: #f9fafb;
  opacity: 0.6;
  cursor: not-allowed;
}

.input-wrapper.error {
  border-color: #ef4444;
}

.input-wrapper.error.focused {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: #111827;
  min-width: 0;
}

.input::placeholder {
  color: #9ca3af;
}

.input:disabled {
  cursor: not-allowed;
}

.textarea {
  resize: vertical;
  font-family: inherit;
  line-height: 1.5;
}

.input-prefix,
.input-suffix,
.input-clear {
  display: flex;
  align-items: center;
  color: #6b7280;
  flex-shrink: 0;
}

.suffix-btn {
  padding: 4px;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: inherit;
  transition: all 0.2s;
}

.suffix-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.input-error {
  margin-top: 6px;
  font-size: 13px;
  color: #ef4444;
}

.input-hint {
  margin-top: 6px;
  font-size: 13px;
  color: #6b7280;
}
</style>
