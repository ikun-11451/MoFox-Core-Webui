// 统一导出所有通用组件
export { default as Modal } from './Modal.vue'
export { default as Button } from './Button.vue'
export { default as Input } from './Input.vue'
export { default as Select } from './Select.vue'
export { default as Switch } from './Switch.vue'
export { default as Toast } from './Toast.vue'

// 导出 Toast 工具函数
export { useToast, setupToast, installToast } from '@/composables/useToast'
