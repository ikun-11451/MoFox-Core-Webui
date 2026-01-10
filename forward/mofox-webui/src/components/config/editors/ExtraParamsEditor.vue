<template>
  <div class="extra-params-editor">
    <div class="editor-header">
      <div class="header-left">
        <Icon icon="lucide:braces" />
        <span class="header-title">额外参数 (extra_params)</span>
        <span class="header-hint">自定义模型参数</span>
      </div>
      <div class="mode-toggle">
        <button
          class="mode-btn"
          :class="{ active: mode === 'form' }"
          @click="mode = 'form'"
          title="表单模式"
        >
          <Icon icon="lucide:list" />
          <span>表单</span>
        </button>
        <button
          class="mode-btn"
          :class="{ active: mode === 'json' }"
          @click="mode = 'json'"
          title="JSON模式"
        >
          <Icon icon="lucide:code" />
          <span>JSON</span>
        </button>
      </div>
    </div>

    <!-- 表单模式 -->
    <div v-if="mode === 'form'" class="form-mode">
      <div v-if="formEntries.length === 0" class="empty-state">
        <Icon icon="lucide:inbox" />
        <span>暂无参数，点击下方添加</span>
      </div>
      <div v-else class="form-entries">
        <div
          v-for="(entry, index) in formEntries"
          :key="index"
          class="form-entry"
        >
          <input
            v-model="entry.key"
            type="text"
            class="entry-input key-input"
            placeholder="参数名"
            @input="updateFromForm"
          />
          <input
            v-model="entry.value"
            type="text"
            class="entry-input value-input"
            placeholder="值 (支持 true/false/数字/字符串)"
            @input="updateFromForm"
          />
          <button
            class="remove-btn"
            @click="removeEntry(index)"
            title="删除"
          >
            <Icon icon="lucide:x" />
          </button>
        </div>
      </div>
      <button class="add-btn" @click="addEntry">
        <Icon icon="lucide:plus" />
        <span>添加参数</span>
      </button>
      <div v-if="formError" class="error-message">
        <Icon icon="lucide:alert-circle" />
        <span>{{ formError }}</span>
      </div>
    </div>

    <!-- JSON 模式 -->
    <div v-if="mode === 'json'" class="json-mode">
      <div class="json-editor-wrapper">
        <textarea
          v-model="jsonText"
          class="json-editor"
          :class="{ error: jsonError }"
          placeholder='例如: {&#10;  "enable_thinking": false,&#10;  "thinking_budget": 256,&#10;  "custom_param": "value"&#10;}'
          rows="8"
          spellcheck="false"
          @input="updateFromJson"
          @blur="validateJson"
        ></textarea>
        <div v-if="jsonError" class="json-error">
          <Icon icon="lucide:alert-circle" />
          <span>{{ jsonError }}</span>
        </div>
      </div>
      <div class="json-tips">
        <Icon icon="lucide:info" />
        <div class="tips-content">
          <strong>提示：</strong>
          <ul>
            <li>必须是有效的 JSON 对象格式</li>
            <li>支持字符串、数字、布尔值 (true/false)</li>
            <li>参数名和字符串值需使用双引号</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { Icon } from '@iconify/vue'

// Props
const props = defineProps<{
  modelValue: Record<string, unknown> | undefined
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: Record<string, unknown> | undefined): void
}>()

// 编辑模式：form 或 json
const mode = ref<'form' | 'json'>('form')

// 表单模式数据
interface FormEntry {
  key: string
  value: string
}

const formEntries = ref<FormEntry[]>([])
const formError = ref('')

// JSON 模式数据
const jsonText = ref('')
const jsonError = ref('')

// 初始化数据
function initializeData() {
  const params = props.modelValue || {}
  
  // 初始化表单模式
  formEntries.value = Object.entries(params).map(([key, value]) => ({
    key,
    value: typeof value === 'string' ? value : JSON.stringify(value)
  }))
  
  // 初始化 JSON 模式
  try {
    jsonText.value = Object.keys(params).length > 0 
      ? JSON.stringify(params, null, 2)
      : ''
    jsonError.value = ''
  } catch (e) {
    jsonText.value = ''
    jsonError.value = '无法序列化当前参数'
  }
}

// 监听 modelValue 变化
watch(() => props.modelValue, () => {
  initializeData()
}, { immediate: true, deep: true })

// 添加表单条目
function addEntry() {
  formEntries.value.push({ key: '', value: '' })
}

// 删除表单条目
function removeEntry(index: number) {
  formEntries.value.splice(index, 1)
  updateFromForm()
}

// 解析值（尝试转换为正确的类型）
function parseValue(value: string): unknown {
  const trimmed = value.trim()
  
  // 空值
  if (trimmed === '') return ''
  
  // 布尔值
  if (trimmed === 'true') return true
  if (trimmed === 'false') return false
  
  // null
  if (trimmed === 'null') return null
  
  // 数字
  if (/^-?\d+$/.test(trimmed)) {
    return parseInt(trimmed, 10)
  }
  if (/^-?\d+\.\d+$/.test(trimmed)) {
    return parseFloat(trimmed)
  }
  
  // 尝试解析为 JSON（支持对象和数组）
  if ((trimmed.startsWith('{') && trimmed.endsWith('}')) ||
      (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
    try {
      return JSON.parse(trimmed)
    } catch {
      // 解析失败，当作字符串
    }
  }
  
  // 默认作为字符串
  return value
}

// 从表单更新
function updateFromForm() {
  formError.value = ''
  
  const result: Record<string, unknown> = {}
  const keys = new Set<string>()
  
  for (const entry of formEntries.value) {
    const key = entry.key.trim()
    
    // 跳过空键
    if (!key) continue
    
    // 检查重复键
    if (keys.has(key)) {
      formError.value = `参数名 "${key}" 重复`
      return
    }
    keys.add(key)
    
    // 解析值
    result[key] = parseValue(entry.value)
  }
  
  // 同步到 JSON 模式
  try {
    jsonText.value = Object.keys(result).length > 0
      ? JSON.stringify(result, null, 2)
      : ''
    jsonError.value = ''
  } catch (e) {
    jsonError.value = '序列化失败'
  }
  
  // 触发更新
  emit('update:modelValue', Object.keys(result).length > 0 ? result : undefined)
}

// 从 JSON 更新
function updateFromJson() {
  // 清除之前的错误
  jsonError.value = ''
}

// 验证 JSON
function validateJson() {
  const trimmed = jsonText.value.trim()
  
  // 空值时清空
  if (!trimmed) {
    formEntries.value = []
    formError.value = ''
    jsonError.value = ''
    emit('update:modelValue', undefined)
    return
  }
  
  try {
    const parsed = JSON.parse(trimmed)
    
    // 必须是对象
    if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
      jsonError.value = 'extra_params 必须是一个对象'
      return
    }
    
    // 更新成功
    jsonError.value = ''
    
    // 同步到表单模式
    formEntries.value = Object.entries(parsed).map(([key, value]) => ({
      key,
      value: typeof value === 'string' ? value : JSON.stringify(value)
    }))
    formError.value = ''
    
    // 触发更新
    emit('update:modelValue', parsed)
    
  } catch (e) {
    jsonError.value = `JSON 解析错误: ${(e as Error).message}`
  }
}

// 计算当前是否有数据
const hasData = computed(() => {
  return props.modelValue && Object.keys(props.modelValue).length > 0
})
</script>

<style scoped>
.extra-params-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
}

/* 编辑器头部 */
.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.header-left svg {
  width: 16px;
  height: 16px;
  color: var(--text-tertiary);
}

.header-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-hint {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-left: auto;
}

/* 模式切换 */
.mode-toggle {
  display: flex;
  gap: 4px;
  background: var(--bg-primary);
  padding: 3px;
  border-radius: var(--radius);
  border: 1px solid var(--border-color);
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: transparent;
  border: none;
  border-radius: calc(var(--radius) - 2px);
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.mode-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.mode-btn.active {
  background: var(--primary);
  color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.mode-btn svg {
  width: 14px;
  height: 14px;
}

/* 表单模式 */
.form-mode {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px;
  color: var(--text-tertiary);
  font-size: 12px;
}

.empty-state svg {
  width: 32px;
  height: 32px;
  opacity: 0.5;
}

.form-entries {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-entry {
  display: flex;
  gap: 8px;
  align-items: center;
}

.entry-input {
  flex: 1;
  padding: 8px 10px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  color: var(--text-primary);
  font-size: 12px;
  outline: none;
  transition: all 0.2s;
}

.entry-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px var(--primary-bg);
}

.entry-input::placeholder {
  color: var(--text-tertiary);
}

.key-input {
  max-width: 150px;
  font-weight: 500;
}

.remove-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: var(--radius);
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.remove-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.add-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px dashed var(--border-color);
  border-radius: var(--radius);
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.add-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--primary-bg);
}

.add-btn svg {
  width: 14px;
  height: 14px;
}

/* JSON 模式 */
.json-mode {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.json-editor-wrapper {
  position: relative;
}

.json-editor {
  width: 100%;
  min-height: 150px;
  padding: 12px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-primary);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  resize: vertical;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.json-editor:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px var(--primary-bg);
}

.json-editor.error {
  border-color: #ef4444;
}

.json-editor::placeholder {
  color: var(--text-tertiary);
  font-style: italic;
}

.json-error {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  padding: 8px 12px;
  font-size: 11px;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius);
}

.json-error svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 11px;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius);
}

.error-message svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

/* JSON 提示 */
.json-tips {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 11px;
  color: var(--text-secondary);
}

.json-tips svg {
  width: 14px;
  height: 14px;
  color: var(--primary);
  flex-shrink: 0;
  margin-top: 2px;
}

.tips-content {
  flex: 1;
}

.tips-content strong {
  color: var(--text-primary);
  font-weight: 600;
}

.tips-content ul {
  margin: 4px 0 0 0;
  padding-left: 16px;
  list-style-type: disc;
}

.tips-content li {
  margin: 2px 0;
}
</style>