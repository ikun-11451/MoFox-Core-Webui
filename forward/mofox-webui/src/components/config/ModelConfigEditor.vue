<template>
  <div class="model-config-editor">
    <!-- 快速操作栏 -->
    <div class="quick-actions">
      <h3>
        <Icon icon="lucide:zap" />
        快速操作
      </h3>
      <div class="action-buttons">
        <button class="action-btn" @click="showAddProviderModal = true">
          <Icon icon="lucide:plus-circle" />
          <span>添加提供商</span>
          <small>配置新的 AI 服务提供商</small>
        </button>
        <button class="action-btn" @click="showAddModelModal = true">
          <Icon icon="lucide:bot" />
          <span>添加模型</span>
          <small>为现有提供商添加模型</small>
        </button>
      </div>
    </div>

    <!-- 提供商列表 -->
    <div class="providers-section">
      <div class="section-header">
        <h3>
          <Icon icon="lucide:cloud" />
          AI 服务提供商
        </h3>
        <span class="provider-count">{{ providers.length }} 个提供商</span>
      </div>
      
      <div v-if="providers.length === 0" class="empty-state">
        <Icon icon="lucide:cloud-off" />
        <p>暂无配置的提供商</p>
        <button class="btn btn-primary" @click="showAddProviderModal = true">
          <Icon icon="lucide:plus" />
          添加第一个提供商
        </button>
      </div>
      
      <div v-else class="providers-grid">
        <div 
          v-for="(provider, index) in providers" 
          :key="index" 
          class="provider-card"
          :class="{ expanded: expandedProvider === index }"
        >
          <div class="provider-header" @click="toggleProvider(index)">
            <div class="provider-icon">
              <Icon :icon="getProviderIcon(provider.name || '')" />
            </div>
            <div class="provider-info">
              <h4>{{ provider.name || '未命名提供商' }}</h4>
              <span class="provider-type">{{ provider.type || 'OpenAI 兼容' }}</span>
            </div>
            <div class="provider-meta">
              <span class="model-count">{{ getModelCount(provider) }} 个模型</span>
              <Icon :icon="expandedProvider === index ? 'lucide:chevron-up' : 'lucide:chevron-down'" />
            </div>
          </div>
          
          <div v-show="expandedProvider === index" class="provider-content">
            <!-- 基础配置 -->
            <div class="config-group">
              <h5>
                <Icon icon="lucide:settings" />
                基础配置
              </h5>
              <div class="config-fields">
                <div class="config-field">
                  <label>
                    提供商名称
                    <span class="field-hint">用于标识此提供商的唯一名称</span>
                  </label>
                  <input 
                    type="text" 
                    class="input" 
                    :value="provider.name"
                    @input="updateProvider(index, 'name', ($event.target as HTMLInputElement).value)"
                    placeholder="例如: OpenAI, Claude, 通义千问"
                  />
                </div>
                <div class="config-field">
                  <label>
                    API 地址
                    <span class="field-hint">提供商的 API 端点地址</span>
                  </label>
                  <input 
                    type="text" 
                    class="input" 
                    :value="provider.base_url"
                    @input="updateProvider(index, 'base_url', ($event.target as HTMLInputElement).value)"
                    placeholder="例如: https://api.openai.com/v1"
                  />
                </div>
                <div class="config-field">
                  <label>
                    API 密钥
                    <span class="field-hint">访问此提供商服务所需的密钥</span>
                  </label>
                  <div class="password-input">
                    <input 
                      :type="showApiKey[index] ? 'text' : 'password'" 
                      class="input" 
                      :value="provider.api_key"
                      @input="updateProvider(index, 'api_key', ($event.target as HTMLInputElement).value)"
                      placeholder="sk-..."
                    />
                    <button class="toggle-visibility" @click="toggleApiKeyVisibility(index)">
                      <Icon :icon="showApiKey[index] ? 'lucide:eye-off' : 'lucide:eye'" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 模型列表 -->
            <div class="config-group">
              <div class="group-header">
                <h5>
                  <Icon icon="lucide:brain" />
                  可用模型
                </h5>
                <button class="btn btn-sm btn-ghost" @click="addModelToProvider(index)">
                  <Icon icon="lucide:plus" />
                  添加模型
                </button>
              </div>
              <div class="models-list">
                <div 
                  v-for="(model, modelIndex) in getProviderModels(provider)" 
                  :key="modelIndex" 
                  class="model-item"
                >
                  <div class="model-info">
                    <span class="model-name">{{ model.model_identifier || model }}</span>
                    <span v-if="model.display_name" class="model-display-name">{{ model.display_name }}</span>
                  </div>
                  <div class="model-actions">
                    <button class="btn-icon" @click="editModel(index, modelIndex, model)">
                      <Icon icon="lucide:edit-2" />
                    </button>
                    <button class="btn-icon danger" @click="removeModel(index, modelIndex)">
                      <Icon icon="lucide:trash-2" />
                    </button>
                  </div>
                </div>
                <div v-if="getProviderModels(provider).length === 0" class="empty-models">
                  <Icon icon="lucide:bot" />
                  <span>暂无模型配置</span>
                </div>
              </div>
            </div>
            
            <!-- 高级设置 -->
            <div class="config-group collapsible">
              <div class="group-header clickable" @click="toggleAdvanced(index)">
                <h5>
                  <Icon icon="lucide:sliders" />
                  高级设置
                </h5>
                <Icon :icon="showAdvanced[index] ? 'lucide:chevron-up' : 'lucide:chevron-down'" />
              </div>
              <div v-show="showAdvanced[index]" class="advanced-fields">
                <div class="config-field">
                  <label>
                    请求超时（秒）
                    <span class="field-hint">API 请求的最大等待时间</span>
                  </label>
                  <input 
                    type="number" 
                    class="input" 
                    :value="provider.timeout || 60"
                    @input="updateProvider(index, 'timeout', parseInt(($event.target as HTMLInputElement).value))"
                  />
                </div>
                <div class="config-field">
                  <label>
                    最大重试次数
                    <span class="field-hint">请求失败时的重试次数</span>
                  </label>
                  <input 
                    type="number" 
                    class="input" 
                    :value="provider.max_retries || 3"
                    @input="updateProvider(index, 'max_retries', parseInt(($event.target as HTMLInputElement).value))"
                  />
                </div>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="provider-actions">
              <button class="btn btn-danger" @click="removeProvider(index)">
                <Icon icon="lucide:trash-2" />
                删除此提供商
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加提供商弹窗 -->
    <div v-if="showAddProviderModal" class="modal-overlay" @click.self="showAddProviderModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>
            <Icon icon="lucide:plus-circle" />
            添加 AI 提供商
          </h3>
          <button class="close-btn" @click="showAddProviderModal = false">
            <Icon icon="lucide:x" />
          </button>
        </div>
        <div class="modal-body">
          <!-- 预设模板 -->
          <div class="preset-providers">
            <h4>选择预设模板</h4>
            <div class="preset-grid">
              <button 
                v-for="preset in providerPresets" 
                :key="preset.name"
                class="preset-btn"
                @click="selectPreset(preset)"
              >
                <Icon :icon="preset.icon" />
                <span>{{ preset.name }}</span>
              </button>
            </div>
          </div>
          
          <div class="divider">
            <span>或手动配置</span>
          </div>
          
          <div class="manual-config">
            <div class="config-field">
              <label>提供商名称</label>
              <input v-model="newProvider.name" type="text" class="input" placeholder="自定义名称" />
            </div>
            <div class="config-field">
              <label>API 地址</label>
              <input v-model="newProvider.base_url" type="text" class="input" placeholder="https://api.example.com/v1" />
            </div>
            <div class="config-field">
              <label>API 密钥</label>
              <input v-model="newProvider.api_key" type="password" class="input" placeholder="你的 API 密钥" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showAddProviderModal = false">取消</button>
          <button class="btn btn-primary" @click="confirmAddProvider" :disabled="!newProvider.name">
            <Icon icon="lucide:check" />
            添加
          </button>
        </div>
      </div>
    </div>

    <!-- 添加模型弹窗 -->
    <div v-if="showAddModelModal" class="modal-overlay" @click.self="showAddModelModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>
            <Icon icon="lucide:bot" />
            添加模型
          </h3>
          <button class="close-btn" @click="showAddModelModal = false">
            <Icon icon="lucide:x" />
          </button>
        </div>
        <div class="modal-body">
          <div class="config-field">
            <label>选择提供商</label>
            <select v-model="newModel.providerIndex" class="input">
              <option v-for="(provider, index) in providers" :key="index" :value="index">
                {{ provider.name || `提供商 ${index + 1}` }}
              </option>
            </select>
          </div>
          <div class="config-field">
            <label>
              模型标识符
              <span class="field-hint">API 调用时使用的模型名称</span>
            </label>
            <input v-model="newModel.model_identifier" type="text" class="input" placeholder="例如: gpt-4, claude-3-opus" />
          </div>
          <div class="config-field">
            <label>
              显示名称
              <span class="field-hint">在界面中显示的友好名称（可选）</span>
            </label>
            <input v-model="newModel.display_name" type="text" class="input" placeholder="例如: GPT-4 Turbo" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showAddModelModal = false">取消</button>
          <button class="btn btn-primary" @click="confirmAddModel" :disabled="!newModel.model_identifier">
            <Icon icon="lucide:check" />
            添加
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'

interface Provider {
  name?: string
  base_url?: string
  api_key?: string
  type?: string
  timeout?: number
  max_retries?: number
  models?: unknown[]
  [key: string]: unknown
}

interface ModelInfo {
  model_identifier?: string
  display_name?: string
  [key: string]: unknown
}

const props = defineProps<{
  parsedData: Record<string, unknown>
  editedValues: Record<string, unknown>
}>()

const emit = defineEmits<{
  (e: 'update', key: string, value: unknown): void
}>()

// 状态
const expandedProvider = ref<number | null>(0)
const showApiKey = ref<Record<number, boolean>>({})
const showAdvanced = ref<Record<number, boolean>>({})
const showAddProviderModal = ref(false)
const showAddModelModal = ref(false)

// 新提供商表单
const newProvider = ref({
  name: '',
  base_url: '',
  api_key: '',
  type: 'openai_compatible'
})

// 新模型表单
const newModel = ref({
  providerIndex: 0,
  model_identifier: '',
  display_name: ''
})

// 预设提供商模板
const providerPresets = [
  { name: 'OpenAI', icon: 'simple-icons:openai', base_url: 'https://api.openai.com/v1', type: 'openai' },
  { name: 'Claude', icon: 'simple-icons:anthropic', base_url: 'https://api.anthropic.com', type: 'anthropic' },
  { name: '通义千问', icon: 'lucide:brain', base_url: 'https://dashscope.aliyuncs.com/api/v1', type: 'qwen' },
  { name: 'Gemini', icon: 'simple-icons:google', base_url: 'https://generativelanguage.googleapis.com', type: 'gemini' },
  { name: 'DeepSeek', icon: 'lucide:brain-circuit', base_url: 'https://api.deepseek.com/v1', type: 'deepseek' },
  { name: '自定义', icon: 'lucide:settings', base_url: '', type: 'openai_compatible' },
]

// 计算提供商列表
const providers = computed(() => {
  // 尝试从不同的数据结构中获取提供商列表
  const data = props.parsedData
  
  // 检查 providers 数组
  if (Array.isArray(data.providers)) {
    return data.providers as Provider[]
  }
  
  // 检查 llm_providers 数组
  if (Array.isArray(data.llm_providers)) {
    return data.llm_providers as Provider[]
  }
  
  // 检查 model 下的 providers
  if (data.model && Array.isArray((data.model as Record<string, unknown>).providers)) {
    return (data.model as Record<string, unknown>).providers as Provider[]
  }
  
  return []
})

// 方法
function toggleProvider(index: number) {
  expandedProvider.value = expandedProvider.value === index ? null : index
}

function toggleApiKeyVisibility(index: number) {
  showApiKey.value[index] = !showApiKey.value[index]
}

function toggleAdvanced(index: number) {
  showAdvanced.value[index] = !showAdvanced.value[index]
}

function getProviderIcon(name: string): string {
  const iconMap: Record<string, string> = {
    'openai': 'simple-icons:openai',
    'claude': 'simple-icons:anthropic',
    'anthropic': 'simple-icons:anthropic',
    'gemini': 'simple-icons:google',
    'google': 'simple-icons:google',
    'qwen': 'lucide:brain',
    '通义': 'lucide:brain',
    'deepseek': 'lucide:brain-circuit',
  }
  
  const lowerName = name.toLowerCase()
  for (const [key, icon] of Object.entries(iconMap)) {
    if (lowerName.includes(key)) {
      return icon
    }
  }
  return 'lucide:cloud'
}

function getModelCount(provider: Provider): number {
  if (Array.isArray(provider.models)) {
    return provider.models.length
  }
  return 0
}

function getProviderModels(provider: Provider): ModelInfo[] {
  if (Array.isArray(provider.models)) {
    return provider.models.map(m => {
      if (typeof m === 'string') {
        return { model_identifier: m }
      }
      return m as ModelInfo
    })
  }
  return []
}

function updateProvider(index: number, key: string, value: unknown) {
  // 构建更新路径
  const basePath = getProvidersPath()
  emit('update', `${basePath}.${index}.${key}`, value)
}

function getProvidersPath(): string {
  const data = props.parsedData
  if (Array.isArray(data.providers)) {
    return 'providers'
  }
  if (Array.isArray(data.llm_providers)) {
    return 'llm_providers'
  }
  if (data.model && Array.isArray((data.model as Record<string, unknown>).providers)) {
    return 'model.providers'
  }
  return 'providers'
}

function selectPreset(preset: typeof providerPresets[0]) {
  newProvider.value = {
    name: preset.name === '自定义' ? '' : preset.name,
    base_url: preset.base_url,
    api_key: '',
    type: preset.type
  }
}

function confirmAddProvider() {
  if (!newProvider.value.name) return
  
  const basePath = getProvidersPath()
  const newProviders = [...providers.value, {
    name: newProvider.value.name,
    base_url: newProvider.value.base_url,
    api_key: newProvider.value.api_key,
    type: newProvider.value.type,
    models: []
  }]
  
  emit('update', basePath, newProviders)
  
  showAddProviderModal.value = false
  newProvider.value = { name: '', base_url: '', api_key: '', type: 'openai_compatible' }
  
  // 展开新添加的提供商
  expandedProvider.value = newProviders.length - 1
}

function removeProvider(index: number) {
  if (!confirm('确定要删除此提供商吗？这将同时删除所有关联的模型配置。')) {
    return
  }
  
  const basePath = getProvidersPath()
  const newProviders = providers.value.filter((_, i) => i !== index)
  emit('update', basePath, newProviders)
  
  if (expandedProvider.value === index) {
    expandedProvider.value = null
  }
}

function addModelToProvider(providerIndex: number) {
  newModel.value.providerIndex = providerIndex
  showAddModelModal.value = true
}

function confirmAddModel() {
  if (!newModel.value.model_identifier) return
  
  const provider = providers.value[newModel.value.providerIndex]
  if (!provider) return
  
  const models = Array.isArray(provider.models) ? [...provider.models] : []
  models.push({
    model_identifier: newModel.value.model_identifier,
    display_name: newModel.value.display_name || newModel.value.model_identifier
  })
  
  const basePath = getProvidersPath()
  emit('update', `${basePath}.${newModel.value.providerIndex}.models`, models)
  
  showAddModelModal.value = false
  newModel.value = { providerIndex: 0, model_identifier: '', display_name: '' }
}

function editModel(providerIndex: number, modelIndex: number, model: ModelInfo) {
  // 简单的编辑实现 - 可以扩展为弹窗
  const newIdentifier = prompt('模型标识符:', model.model_identifier || '')
  if (newIdentifier === null) return
  
  const provider = providers.value[providerIndex]
  if (!provider || !Array.isArray(provider.models)) return
  
  const models = [...provider.models]
  if (typeof models[modelIndex] === 'object') {
    models[modelIndex] = { ...models[modelIndex] as object, model_identifier: newIdentifier }
  } else {
    models[modelIndex] = { model_identifier: newIdentifier }
  }
  
  const basePath = getProvidersPath()
  emit('update', `${basePath}.${providerIndex}.models`, models)
}

function removeModel(providerIndex: number, modelIndex: number) {
  if (!confirm('确定要删除此模型吗？')) return
  
  const provider = providers.value[providerIndex]
  if (!provider || !Array.isArray(provider.models)) return
  
  const models = provider.models.filter((_, i) => i !== modelIndex)
  
  const basePath = getProvidersPath()
  emit('update', `${basePath}.${providerIndex}.models`, models)
}

// 初始化
watch(() => props.parsedData, () => {
  // 如果有提供商，默认展开第一个
  if (providers.value.length > 0 && expandedProvider.value === null) {
    expandedProvider.value = 0
  }
}, { immediate: true })
</script>

<style scoped>
.model-config-editor {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 快速操作栏 */
.quick-actions {
  background: linear-gradient(135deg, var(--primary-bg), rgba(139, 92, 246, 0.1));
  border-radius: var(--radius-lg);
  padding: 20px;
  border: 1px solid var(--border-color);
}

.quick-actions h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.quick-actions h3 svg {
  color: var(--primary);
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.action-btn svg {
  font-size: 24px;
  color: var(--primary);
}

.action-btn span {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.action-btn small {
  font-size: 12px;
  color: var(--text-tertiary);
}

/* 提供商区域 */
.providers-section {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.section-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.provider-count {
  font-size: 12px;
  color: var(--text-tertiary);
  padding: 4px 10px;
  background: var(--bg-primary);
  border-radius: var(--radius-full);
}

.providers-grid {
  display: flex;
  flex-direction: column;
}

/* 提供商卡片 */
.provider-card {
  border-bottom: 1px solid var(--border-color);
}

.provider-card:last-child {
  border-bottom: none;
}

.provider-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.provider-header:hover {
  background: var(--bg-secondary);
}

.provider-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary), #6d28d9);
  border-radius: var(--radius);
  color: white;
  font-size: 20px;
}

.provider-info {
  flex: 1;
}

.provider-info h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.provider-type {
  font-size: 12px;
  color: var(--text-tertiary);
}

.provider-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
}

.model-count {
  font-size: 12px;
  padding: 4px 10px;
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
}

.provider-content {
  padding: 0 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 配置组 */
.config-group {
  background: var(--bg-secondary);
  border-radius: var(--radius);
  padding: 16px;
}

.config-group h5 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.group-header h5 {
  margin: 0;
}

.group-header.clickable {
  cursor: pointer;
  margin-bottom: 0;
  padding: 4px 0;
}

.group-header.clickable:hover {
  color: var(--primary);
}

.config-fields {
  display: grid;
  gap: 16px;
}

.config-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-field label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.field-hint {
  font-size: 11px;
  font-weight: 400;
  color: var(--text-tertiary);
}

.input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  transition: all var(--transition-fast);
}

.input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-bg);
}

select.input {
  cursor: pointer;
}

.password-input {
  position: relative;
  display: flex;
}

.password-input .input {
  padding-right: 44px;
}

.toggle-visibility {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.toggle-visibility:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

/* 模型列表 */
.models-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.model-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: var(--radius);
}

.model-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.model-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
}

.model-display-name {
  font-size: 11px;
  color: var(--text-tertiary);
}

.model-actions {
  display: flex;
  gap: 4px;
}

.btn-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-icon:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-icon.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.empty-models {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: var(--text-tertiary);
  font-size: 13px;
}

.advanced-fields {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.provider-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

/* 按钮样式 */
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-hover);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
}

.btn-ghost:hover:not(:disabled) {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-danger {
  background: transparent;
  color: #ef4444;
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.1);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px;
  color: var(--text-tertiary);
}

.empty-state svg {
  font-size: 48px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  animation: modalIn 0.2s ease;
  display: flex;
  flex-direction: column;
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.close-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

/* 预设模板 */
.preset-providers h4 {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.preset-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.preset-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.preset-btn:hover {
  border-color: var(--primary);
  background: var(--primary-bg);
}

.preset-btn svg {
  font-size: 24px;
  color: var(--text-secondary);
}

.preset-btn:hover svg {
  color: var(--primary);
}

.preset-btn span {
  font-size: 12px;
  color: var(--text-primary);
}

.divider {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 20px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-color);
}

.divider span {
  font-size: 12px;
  color: var(--text-tertiary);
}

.manual-config {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
