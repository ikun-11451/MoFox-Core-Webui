<template>
  <div class="expression-rules-editor">
    <div class="editor-header">
      <h4>
        <Icon icon="lucide:sparkles" />
        表达学习规则配置
      </h4>
      <p class="editor-hint">为不同聊天流配置独立的表达学习规则</p>
    </div>
    
    <div class="rules-list">
      <div 
        v-for="(rule, index) in rules" 
        :key="index" 
        class="rule-card"
        :class="{ 'global-rule': !rule.chat_stream_id }"
      >
        <div class="rule-header">
          <span class="rule-label">
            <Icon :icon="!rule.chat_stream_id ? 'lucide:globe' : 'lucide:message-square'" />
            {{ !rule.chat_stream_id ? '全局规则' : '聊天流规则' }}
          </span>
          <button 
            v-if="index > 0" 
            class="btn-icon delete-btn" 
            @click="removeRule(index)" 
            title="删除规则"
          >
            <Icon icon="lucide:trash-2" />
          </button>
        </div>
        
        <div class="rule-fields">
          <div class="field-row">
            <label>聊天流ID</label>
            <input 
              type="text" 
              class="input"
              :value="rule.chat_stream_id || ''"
              @input="updateRule(index, 'chat_stream_id', ($event.target as HTMLInputElement).value)"
              placeholder='留空为全局，格式: "platform:id:type"'
            />
          </div>
          
          <div class="field-row">
            <label>共享组</label>
            <input 
              type="text" 
              class="input"
              :value="rule.group || ''"
              @input="updateRule(index, 'group', ($event.target as HTMLInputElement).value)"
              placeholder="相同组的聊天会共享学习到的表达方式"
            />
          </div>
          
          <div class="field-row switches">
            <label class="switch-label">
              <input 
                type="checkbox" 
                :checked="rule.use_expression !== false"
                @change="updateRule(index, 'use_expression', ($event.target as HTMLInputElement).checked)"
              />
              <span>使用表达</span>
            </label>
            <label class="switch-label">
              <input 
                type="checkbox" 
                :checked="rule.learn_expression !== false"
                @change="updateRule(index, 'learn_expression', ($event.target as HTMLInputElement).checked)"
              />
              <span>学习表达</span>
            </label>
          </div>
          
          <div class="field-row">
            <label>学习强度</label>
            <div class="slider-input">
              <input 
                type="range" 
                :value="rule.learning_strength ?? 1.0"
                @input="updateRule(index, 'learning_strength', parseFloat(($event.target as HTMLInputElement).value))"
                min="0"
                max="3"
                step="0.1"
              />
              <span class="slider-value">{{ (rule.learning_strength ?? 1.0).toFixed(1) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="rules.length === 0" class="empty-state">
        <Icon icon="lucide:list-x" />
        <p>暂无表达规则</p>
      </div>
    </div>
    
    <button class="btn btn-outline add-btn" @click="addRule">
      <Icon icon="lucide:plus" />
      添加规则
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'

interface ExpressionRule {
  chat_stream_id?: string
  group?: string
  use_expression?: boolean
  learn_expression?: boolean
  learning_strength?: number
}

const props = defineProps<{
  value: unknown
}>()

const emit = defineEmits<{
  (e: 'update', value: ExpressionRule[]): void
}>()

// 解析规则列表
const rules = computed(() => {
  if (Array.isArray(props.value)) {
    return props.value as ExpressionRule[]
  }
  return []
})

// 添加规则
function addRule() {
  const newRules = [...rules.value, {
    chat_stream_id: '',
    use_expression: true,
    learn_expression: true,
    learning_strength: 1.0
  }]
  emit('update', newRules)
}

// 删除规则
function removeRule(index: number) {
  const newRules = rules.value.filter((_, i) => i !== index)
  emit('update', newRules)
}

// 更新规则
function updateRule(index: number, field: keyof ExpressionRule, value: unknown) {
  const newRules = rules.value.map((rule, i) => {
    if (i === index) {
      return { ...rule, [field]: value }
    }
    return rule
  })
  emit('update', newRules)
}
</script>

<style scoped>
.expression-rules-editor {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.editor-header h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.editor-header h4 svg {
  color: #8b5cf6;
}

.editor-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0;
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rule-card {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
}

.rule-card.global-rule {
  border-color: var(--primary);
  background: var(--primary-bg);
}

.rule-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.rule-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.rule-label svg {
  color: var(--primary);
}

.delete-btn {
  padding: 4px;
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  border-radius: var(--radius);
  transition: all var(--transition-fast);
}

.delete-btn:hover {
  background: var(--danger-bg);
  color: var(--danger);
}

.rule-fields {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-row label {
  font-size: 12px;
  color: var(--text-secondary);
}

.field-row.switches {
  flex-direction: row;
  gap: 16px;
}

.switch-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-primary);
  cursor: pointer;
}

.switch-label input {
  width: 16px;
  height: 16px;
  accent-color: var(--primary);
}

.input {
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  color: var(--text-primary);
  font-family: 'Roboto Mono', 'Noto Sans SC', sans-serif !important;
  font-size: 13px;
}

.input:focus {
  border-color: var(--primary);
  outline: none;
}

.slider-input {
  display: flex;
  align-items: center;
  gap: 12px;
}

.slider-input input[type="range"] {
  flex: 1;
  height: 4px;
  accent-color: var(--primary);
}

.slider-value {
  min-width: 32px;
  text-align: right;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px;
  color: var(--text-tertiary);
}

.empty-state svg {
  font-size: 24px;
}

.add-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px dashed var(--border-color);
  border-radius: var(--radius);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.add-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--primary-bg);
}
</style>
