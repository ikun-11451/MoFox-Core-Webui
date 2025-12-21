<template>
  <div class="select-wrapper" :class="{ disabled, error: !!error, open: isOpen }">
    <div 
      class="select-trigger"
      :class="{ focused: isOpen }"
      @click="toggleDropdown"
    >
      <div class="select-value">
        <slot name="selected" :option="selectedOption">
          {{ selectedLabel || placeholder }}
        </slot>
      </div>
      <Icon 
        icon="lucide:chevron-down" 
        class="select-icon"
        :class="{ rotated: isOpen }"
      />
    </div>
    
    <Transition name="dropdown">
      <div v-if="isOpen" class="select-dropdown" @click.stop>
        <div v-if="searchable" class="select-search">
          <Input
            v-model="searchQuery"
            placeholder="搜索..."
            prefix="lucide:search"
            @click.stop
          />
        </div>
        
        <div class="select-options">
          <div
            v-for="option in filteredOptions"
            :key="getOptionValue(option)"
            class="select-option"
            :class="{ 
              selected: isSelected(option),
              disabled: isOptionDisabled(option)
            }"
            @click="selectOption(option)"
          >
            <slot name="option" :option="option">
              {{ getOptionLabel(option) }}
            </slot>
            <Icon 
              v-if="isSelected(option)" 
              icon="lucide:check" 
              class="check-icon"
            />
          </div>
          
          <div v-if="filteredOptions.length === 0" class="select-empty">
            暂无选项
          </div>
        </div>
      </div>
    </Transition>
  </div>
  
  <div v-if="error" class="select-error">{{ error }}</div>
  <div v-else-if="hint" class="select-hint">{{ hint }}</div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { Icon } from '@iconify/vue'
import Input from './Input.vue'

interface Props {
  modelValue: any
  options: any[]
  placeholder?: string
  disabled?: boolean
  searchable?: boolean
  valueKey?: string
  labelKey?: string
  disabledKey?: string
  error?: string
  hint?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请选择',
  disabled: false,
  searchable: false,
  valueKey: 'value',
  labelKey: 'label',
  disabledKey: 'disabled'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: any): void
  (e: 'change', value: any): void
}>()

const isOpen = ref(false)
const searchQuery = ref('')

const filteredOptions = computed(() => {
  if (!props.searchable || !searchQuery.value) {
    return props.options
  }
  
  const query = searchQuery.value.toLowerCase()
  return props.options.filter(option => {
    const label = getOptionLabel(option).toLowerCase()
    return label.includes(query)
  })
})

const selectedOption = computed(() => {
  return props.options.find(option => 
    getOptionValue(option) === props.modelValue
  )
})

const selectedLabel = computed(() => {
  if (selectedOption.value) {
    return getOptionLabel(selectedOption.value)
  }
  return ''
})

function getOptionValue(option: any): any {
  if (typeof option === 'object' && option !== null) {
    return option[props.valueKey]
  }
  return option
}

function getOptionLabel(option: any): string {
  if (typeof option === 'object' && option !== null) {
    return String(option[props.labelKey] || option[props.valueKey] || '')
  }
  return String(option)
}

function isOptionDisabled(option: any): boolean {
  if (typeof option === 'object' && option !== null) {
    return Boolean(option[props.disabledKey])
  }
  return false
}

function isSelected(option: any): boolean {
  return getOptionValue(option) === props.modelValue
}

function toggleDropdown() {
  if (!props.disabled) {
    isOpen.value = !isOpen.value
    if (isOpen.value) {
      searchQuery.value = ''
    }
  }
}

function selectOption(option: any) {
  if (!isOptionDisabled(option)) {
    const value = getOptionValue(option)
    emit('update:modelValue', value)
    emit('change', value)
    isOpen.value = false
  }
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.select-wrapper')) {
    isOpen.value = false
  }
}

watch(isOpen, (newValue) => {
  if (newValue) {
    document.addEventListener('click', handleClickOutside)
  } else {
    document.removeEventListener('click', handleClickOutside)
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.select-wrapper {
  position: relative;
  width: 100%;
}

.select-wrapper.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.select-wrapper.disabled .select-trigger {
  cursor: not-allowed;
  background: #f9fafb;
}

.select-trigger.focused,
.select-wrapper.open .select-trigger {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.select-wrapper.error .select-trigger {
  border-color: #ef4444;
}

.select-wrapper.error .select-trigger.focused {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.select-value {
  flex: 1;
  font-size: 14px;
  color: #111827;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.select-trigger:not(.has-value) .select-value {
  color: #9ca3af;
}

.select-icon {
  flex-shrink: 0;
  color: #6b7280;
  transition: transform 0.2s;
}

.select-icon.rotated {
  transform: rotate(180deg);
}

.select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  max-height: 300px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.select-search {
  padding: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.select-options {
  overflow-y: auto;
  flex: 1;
}

.select-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
  color: #111827;
}

.select-option:hover:not(.disabled) {
  background: #f3f4f6;
}

.select-option.selected {
  background: #eff6ff;
  color: #3b82f6;
  font-weight: 500;
}

.select-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.check-icon {
  flex-shrink: 0;
  color: #3b82f6;
}

.select-empty {
  padding: 20px;
  text-align: center;
  color: #9ca3af;
  font-size: 14px;
}

.select-error {
  margin-top: 6px;
  font-size: 13px;
  color: #ef4444;
}

.select-hint {
  margin-top: 6px;
  font-size: 13px;
  color: #6b7280;
}

/* 下拉动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
