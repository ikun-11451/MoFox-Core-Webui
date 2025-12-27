<template>
  <div class="model-config-step">
    <div class="card m3-card">
      <div class="step-header">
        <h2 class="step-title">
          <span class="material-symbols-rounded">psychology</span>
          AI 模型配置
        </h2>
        <p class="step-description">配置 SiliconFlow API 以启用 AI 功能</p>
      </div>
      
      <form class="config-form" @submit.prevent="handleSubmit">
        <!-- API Key -->
        <div class="form-field">
          <label class="field-label">
            <span class="material-symbols-rounded">key</span>
            SiliconFlow API Key
          </label>
          <div class="input-with-action">
            <input
              v-model="formData.api_key"
              @input="handleApiKeyInput"
              :type="showApiKey ? 'text' : 'password'"
              class="m3-input"
              placeholder="sk-..."
              required
            />
            <button
              type="button"
              class="icon-button"
              @click="showApiKey = !showApiKey"
              :aria-label="showApiKey ? '隐藏密钥' : '显示密钥'"
            >
              <span class="material-symbols-rounded">
                {{ showApiKey ? 'visibility_off' : 'visibility' }}
              </span>
            </button>
          </div>
          <span class="field-hint">
            访问
            <a href="https://cloud.siliconflow.cn/account/ak" target="_blank" class="link">
              SiliconFlow 控制台
            </a>
            获取 API Key
          </span>
        </div>
        
        <!-- 信息卡片 -->
        <div class="info-card">
          <div class="info-icon">
            <span class="material-symbols-rounded">info</span>
          </div>
          <div class="info-content">
            <h3>关于 SiliconFlow</h3>
            <p>
              SiliconFlow 提供了多种高质量的开源 AI 模型，包括 DeepSeek-V3、Qwen 等。
              本系统默认配置了适合的模型组合。
            </p>
            <ul>
              <li>✨ 新用户赠送免费额度</li>
              <li>💰 按需付费，价格透明</li>
              <li>🚀 响应速度快，稳定性高</li>
            </ul>
          </div>
        </div>
        
        <!-- 按钮组 -->
        <div class="button-group">
          <button type="button" class="m3-button outlined" @click="$emit('skip')" :disabled="loading">
            <span>跳过此步</span>
          </button>
          <button type="submit" class="m3-button filled" :disabled="loading">
            <span v-if="!loading">验证并继续</span>
            <span v-else>验证中...</span>
            <span class="material-symbols-rounded">arrow_forward</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { saveModelConfig, getModelConfig, validateApiKey, type ModelConfigRequest } from '@/api/initialization'

const emit = defineEmits<{
  next: []
  skip: []
  toast: [message: string]
}>()

const loading = ref(false)
const showApiKey = ref(false)

function handleApiKeyInput() {
  if (formData.value.api_key.toLowerCase() === 'mofox') {
    emit('toast', '嘿嘿，这可不是真的 API Key 哦～')
  }
}

// 表单数据
const formData = ref<ModelConfigRequest>({
  api_key: '',
  provider_name: 'SiliconFlow',
  base_url: 'https://api.siliconflow.cn/v1'
})

// 加载现有配置
async function loadExistingConfig() {
  try {
    console.log('[ModelConfigStep] 正在加载现有配置...')
    const result = await getModelConfig()
    console.log('[ModelConfigStep] API响应:', result)
    
    // 后端返回的数据在 result.data.data 中（双层嵌套）
    const configData = (result.data as any)?.data
    
    if (result.success && configData) {
      console.log('[ModelConfigStep] 加载配置数据:', configData)
      
      // 只在有实际数据时才填充表单
      if (configData.api_key) {
        formData.value.api_key = configData.api_key
      }
      if (configData.provider_name) {
        formData.value.provider_name = configData.provider_name
      }
      if (configData.base_url) {
        formData.value.base_url = configData.base_url
      }
      
      console.log('[ModelConfigStep] 配置加载完成')
    } else {
      console.log('[ModelConfigStep] 无现有配置数据')
    }
  } catch (error) {
    console.error('[ModelConfigStep] 加载模型配置失败:', error)
  }
}

onMounted(() => {
  loadExistingConfig()
})

// 提交表单
async function handleSubmit() {
  loading.value = true
  
  try {
    // 先验证 API Key 格式
    console.log('[ModelConfigStep] 正在验证 API Key...',)
    const validationResult = await validateApiKey(formData.value.api_key)
    
    if (!validationResult.success || !validationResult.data?.valid) {
      alert('API Key 格式不正确：' + (validationResult.data?.message || '请检查输入'))
      loading.value = false
      return
    }
    
    // 保存配置
    const result = await saveModelConfig(formData.value)
    
    if (result.success) {
      emit('next')
    } else {
      alert('保存失败：' + (result.error || '未知错误'))
    }
  } catch (error) {
    console.error('保存模型配置失败:', error)
    alert('保存失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.model-config-step {
  display: flex;
  justify-content: center;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  width: 100%;
  max-width: 700px;
  padding: 40px;
  background: var(--md-sys-color-surface);
  border-radius: 28px;
  box-shadow: var(--md-sys-elevation-2);
}

/* 步骤头部 */
.step-header {
  margin-bottom: 32px;
  text-align: center;
}

.step-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin: 0 0 8px 0;
}

.step-title .material-symbols-rounded {
  font-size: 32px;
  color: var(--md-sys-color-primary);
}

.step-description {
  font-size: 16px;
  color: var(--md-sys-color-on-surface-variant);
  margin: 0;
}

/* 表单 */
.config-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.field-label .material-symbols-rounded {
  font-size: 20px;
  color: var(--md-sys-color-primary);
}

.input-with-action {
  position: relative;
  display: flex;
  align-items: center;
}

.m3-input {
  width: 100%;
  padding: 14px 48px 14px 16px;
  font-size: 16px;
  font-family: inherit;
  color: var(--md-sys-color-on-surface);
  background: var(--md-sys-color-surface-variant);
  border: 2px solid transparent;
  border-radius: 12px;
  outline: none;
  transition: all 0.2s ease;
}

.m3-input:focus {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-surface);
}

.icon-button {
  position: absolute;
  right: 8px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--md-sys-color-on-surface-variant);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.icon-button:hover {
  background: var(--md-sys-color-surface-variant);
}

.icon-button .material-symbols-rounded {
  font-size: 20px;
}

.field-hint {
  font-size: 12px;
  color: var(--md-sys-color-on-surface-variant);
  margin-left: 4px;
}

.link {
  color: var(--md-sys-color-primary);
  text-decoration: none;
  font-weight: 600;
}

.link:hover {
  text-decoration: underline;
}

/* 信息卡片 */
.info-card {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: var(--md-sys-color-tertiary-container);
  border-radius: 16px;
}

.info-icon {
  flex-shrink: 0;
}

.info-icon .material-symbols-rounded {
  font-size: 32px;
  color: var(--md-sys-color-on-tertiary-container);
}

.info-content h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--md-sys-color-on-tertiary-container);
  margin: 0 0 8px 0;
}

.info-content p {
  font-size: 14px;
  line-height: 1.6;
  color: var(--md-sys-color-on-tertiary-container);
  margin: 0 0 12px 0;
}

.info-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-content li {
  font-size: 14px;
  color: var(--md-sys-color-on-tertiary-container);
}

/* 按钮组 */
.button-group {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 16px;
}

.m3-button {
  padding: 12px 28px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 100px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.m3-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.m3-button.filled {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  box-shadow: var(--md-sys-elevation-1);
}

.m3-button.filled:hover:not(:disabled) {
  box-shadow: var(--md-sys-elevation-2);
  transform: scale(1.02);
}

.m3-button.outlined {
  background: transparent;
  color: var(--md-sys-color-primary);
  border: 2px solid var(--md-sys-color-outline);
}

.m3-button.outlined:hover:not(:disabled) {
  background: var(--md-sys-color-surface-variant);
}

.m3-button .material-symbols-rounded {
  font-size: 20px;
}

/* 响应式 */
@media (max-width: 768px) {
  .card {
    padding: 32px 24px;
  }
  
  .step-title {
    font-size: 24px;
  }
  
  .info-card {
    flex-direction: column;
  }
  
  .button-group {
    flex-direction: column;
  }
}
</style>
