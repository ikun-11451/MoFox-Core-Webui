<template>
  <div class="plugin-config-view">
    <!-- 顶部操作栏 -->
    <header class="config-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <Icon icon="lucide:arrow-left" />
        </button>
        <Icon icon="lucide:puzzle" class="header-icon" />
        <div class="header-info">
          <h1>{{ configInfo?.display_name || '插件配置' }}</h1>
          <p>{{ getShortPath(decodedPath) }}</p>
        </div>
      </div>
      <div class="header-actions">
        <div class="editor-tabs">
          <button 
            :class="['tab-btn', { active: editorMode === 'visual' }]"
            @click="editorMode = 'visual'"
          >
            <Icon icon="lucide:layout-grid" />
            可视化
          </button>
          <button 
            :class="['tab-btn', { active: editorMode === 'source' }]"
            @click="editorMode = 'source'"
          >
            <Icon icon="lucide:code" />
            源码
          </button>
        </div>
        <button class="btn btn-ghost" @click="showBackupsModal = true">
          <Icon icon="lucide:history" />
          备份
        </button>
        <button 
          class="btn btn-primary" 
          @click="saveCurrentConfig" 
          :disabled="saving || !hasChanges"
        >
          <Icon :icon="saving ? 'lucide:loader-2' : 'lucide:save'" :class="{ spinning: saving }" />
          {{ saving ? '保存中...' : '保存配置' }}
        </button>
      </div>
    </header>

    <!-- 可视化编辑模式 -->
    <div v-if="editorMode === 'visual'" class="visual-editor">
      <div v-if="loading" class="loading-state">
        <Icon icon="lucide:loader-2" class="spinning" />
        加载配置中...
      </div>
      <div v-else-if="loadError" class="error-state">
        <Icon icon="lucide:alert-circle" />
        {{ loadError }}
      </div>
      <template v-else>
        <!-- 配置导航栏 -->
        <div class="config-nav-bar" v-if="configSchema.length > 1">
          <div class="nav-tabs">
            <button
              v-for="(section, idx) in configSchema"
              :key="section.name"
              class="nav-tab"
              :class="{ active: activeSection === idx }"
              @click="activeSection = idx"
            >
              {{ section.display_name || section.name }}
            </button>
          </div>
        </div>

        <!-- 配置内容 -->
        <div class="config-content">
          <div v-if="currentSection" class="config-section">
            <div class="section-header" v-if="configSchema.length > 1">
              <h3>{{ currentSection.display_name || currentSection.name }}</h3>
              <span class="field-count">{{ currentSection.fields.length }} 项配置</span>
            </div>
            <div class="fields-list">
              <div 
                v-for="field in currentSection.fields" 
                :key="field.full_key" 
                class="field-card"
                :class="{ inline: field.type === 'boolean' }"
              >
                <!-- Boolean 类型 -->
                <template v-if="field.type === 'boolean'">
                  <div class="field-left">
                    <div class="field-header">
                      <span class="field-name">{{ field.key }}</span>
                    </div>
                    <div v-if="field.description" class="field-description">
                      {{ field.description }}
                    </div>
                  </div>
                  <label class="toggle-switch">
                    <input 
                      type="checkbox" 
                      :checked="Boolean(getFieldValue(field.full_key))"
                      @change="updateFieldValue(field.full_key, ($event.target as HTMLInputElement).checked)"
                    />
                    <span class="toggle-slider"></span>
                  </label>
                </template>
                
                <!-- 其他类型 -->
                <template v-else>
                  <div class="field-header">
                    <span class="field-name">{{ field.key }}</span>
                    <span class="field-type">{{ field.type }}</span>
                  </div>
                  <div v-if="field.description" class="field-description">
                    {{ field.description }}
                  </div>
                  <div class="field-input">
                    <FieldEditor 
                      :field="field"
                      :value="getFieldValue(field.full_key)"
                      @update="(v: unknown) => updateFieldValue(field.full_key, v)"
                    />
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- 源码编辑模式 (Monaco Editor) -->
    <div v-else class="source-editor">
      <div class="source-toolbar">
        <span class="file-path">
          <Icon icon="lucide:file-text" />
          {{ decodedPath }}
        </span>
        <div class="toolbar-actions">
          <button class="btn btn-sm btn-ghost" @click="formatSource">
            <Icon icon="lucide:align-left" />
            格式化
          </button>
        </div>
      </div>
      <div class="monaco-container">
        <vue-monaco-editor
          v-model:value="sourceContent"
          :language="getEditorLanguage(decodedPath)"
          :theme="isDarkMode ? 'vs-dark' : 'vs'"
          :options="monacoOptions"
          @mount="onEditorMount"
        />
      </div>
      <div v-if="validationError" class="validation-error">
        <Icon icon="lucide:alert-triangle" />
        {{ validationError }}
      </div>
    </div>

    <!-- 备份管理弹窗 -->
    <div v-if="showBackupsModal" class="modal-overlay" @click.self="showBackupsModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>
            <Icon icon="lucide:history" />
            备份管理
          </h3>
          <button class="close-btn" @click="showBackupsModal = false">
            <Icon icon="lucide:x" />
          </button>
        </div>
        <div class="modal-body">
          <div v-if="backupsLoading" class="loading-state">
            <Icon icon="lucide:loader-2" class="spinning" />
            加载备份列表...
          </div>
          <div v-else-if="backups.length === 0" class="empty-state">
            <Icon icon="lucide:archive-x" />
            暂无备份
          </div>
          <div v-else class="backup-list">
            <div v-for="backup in backups" :key="backup.name" class="backup-item">
              <div class="backup-info">
                <span class="backup-name">{{ backup.name }}</span>
                <span class="backup-meta">
                  {{ backup.created_at }} · {{ formatSize(backup.size) }}
                </span>
              </div>
              <button 
                class="btn btn-sm btn-ghost" 
                @click="restoreBackup(backup.name)"
                :disabled="restoringBackup === backup.name"
              >
                <Icon :icon="restoringBackup === backup.name ? 'lucide:loader-2' : 'lucide:rotate-ccw'" 
                      :class="{ spinning: restoringBackup === backup.name }" />
                恢复
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast 提示 -->
    <div v-if="toast.show" :class="['toast', toast.type]">
      <Icon :icon="toast.type === 'success' ? 'lucide:check-circle' : 'lucide:alert-circle'" />
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, shallowRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'
import type { editor } from 'monaco-editor'
import {
  getConfigList,
  getConfigContent,
  getConfigSchema,
  saveConfig,
  updateConfig,
  getConfigBackups,
  restoreConfigBackup,
  type ConfigFileInfo,
  type ConfigSection,
  type ConfigBackupInfo
} from '@/api'
import FieldEditor from '@/components/config/FieldEditor.vue'

const route = useRoute()
const router = useRouter()

// Props
const props = defineProps<{
  pluginPath?: string
}>()

// Monaco Editor 配置
const monacoOptions: editor.IStandaloneEditorConstructionOptions = {
  minimap: { enabled: true },
  fontSize: 14,
  lineNumbers: 'on',
  roundedSelection: true,
  scrollBeyondLastLine: false,
  automaticLayout: true,
  tabSize: 2,
  wordWrap: 'on',
  folding: true,
  lineDecorationsWidth: 10,
  lineNumbersMinChars: 3,
  renderLineHighlight: 'all',
  scrollbar: {
    verticalScrollbarSize: 10,
    horizontalScrollbarSize: 10
  }
}

// Editor 实例
const editorInstance = shallowRef<editor.IStandaloneCodeEditor | null>(null)

// 解码的路径
const decodedPath = computed(() => {
  const path = props.pluginPath || route.params.pluginPath as string
  return decodeURIComponent(path || '')
})

// 状态
const loading = ref(true)
const saving = ref(false)
const loadError = ref('')
const editorMode = ref<'visual' | 'source'>('visual')
const isDarkMode = ref(true)
const activeSection = ref(0)

// 配置数据
const configInfo = ref<ConfigFileInfo | null>(null)
const configSchema = ref<ConfigSection[]>([])
const editedValues = ref<Record<string, unknown>>({})
const originalParsed = ref<Record<string, unknown>>({})

// 源码编辑状态
const sourceContent = ref('')
const originalContent = ref('')
const validationError = ref('')

// 备份相关
const showBackupsModal = ref(false)
const backups = ref<ConfigBackupInfo[]>([])
const backupsLoading = ref(false)
const restoringBackup = ref('')

// Toast 提示
const toast = ref({ show: false, message: '', type: 'success' as 'success' | 'error' })

// 计算属性
const hasChanges = computed(() => {
  if (editorMode.value === 'source') {
    return sourceContent.value !== originalContent.value
  }
  return Object.keys(editedValues.value).length > 0
})

const currentSection = computed(() => {
  return configSchema.value[activeSection.value]
})

// 方法
function getShortPath(path: string): string {
  const parts = path.split(/[/\\]/)
  if (parts.length > 3) {
    return '...' + parts.slice(-3).join('/')
  }
  return path
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function getEditorLanguage(path: string): string {
  if (path.endsWith('.toml')) return 'ini'
  if (path.endsWith('.json')) return 'json'
  if (path.endsWith('.yaml') || path.endsWith('.yml')) return 'yaml'
  return 'plaintext'
}

function onEditorMount(editor: editor.IStandaloneCodeEditor) {
  editorInstance.value = editor
}

function formatSource() {
  if (editorInstance.value) {
    editorInstance.value.getAction('editor.action.formatDocument')?.run()
  }
}

function goBack() {
  router.push('/dashboard/plugin-config')
}

async function loadConfig() {
  if (!decodedPath.value) {
    loadError.value = '未指定配置文件路径'
    loading.value = false
    return
  }
  
  loading.value = true
  loadError.value = ''
  
  try {
    // 获取配置列表，找到对应的配置信息
    const listRes = await getConfigList()
    if (listRes.success && listRes.data) {
      configInfo.value = listRes.data.configs.find((c: ConfigFileInfo) => c.path === decodedPath.value) || null
    }
    
    // 加载配置内容
    const contentRes = await getConfigContent(decodedPath.value)
    if (contentRes.success && contentRes.data) {
      sourceContent.value = contentRes.data.content || ''
      originalContent.value = contentRes.data.content || ''
      originalParsed.value = contentRes.data.parsed || {}
    } else {
      loadError.value = '加载配置内容失败'
      return
    }
    
    // 加载配置结构
    const schemaRes = await getConfigSchema(decodedPath.value)
    if (schemaRes.success && schemaRes.data?.success) {
      configSchema.value = schemaRes.data.sections
    }
  } catch (e) {
    loadError.value = '加载配置时发生错误'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function getFieldValue(fullKey: string): unknown {
  if (fullKey in editedValues.value) {
    return editedValues.value[fullKey]
  }
  
  const keys = fullKey.split('.')
  let current: unknown = originalParsed.value
  for (const key of keys) {
    if (current && typeof current === 'object' && key in (current as Record<string, unknown>)) {
      current = (current as Record<string, unknown>)[key]
    } else {
      return undefined
    }
  }
  return current
}

function updateFieldValue(fullKey: string, value: unknown) {
  editedValues.value[fullKey] = value
}

async function saveCurrentConfig() {
  if (!decodedPath.value) return
  
  saving.value = true
  try {
    if (editorMode.value === 'source') {
      const res = await saveConfig(decodedPath.value, sourceContent.value)
      if (res.success && res.data?.success) {
        originalContent.value = sourceContent.value
        showToast('配置已保存', 'success')
        await loadConfig()
      } else {
        showToast(res.data?.error || '保存失败', 'error')
      }
    } else {
      if (Object.keys(editedValues.value).length === 0) {
        showToast('没有需要保存的更改', 'error')
        return
      }
      
      const res = await updateConfig(decodedPath.value, editedValues.value)
      if (res.success && res.data?.success) {
        editedValues.value = {}
        showToast('配置已保存', 'success')
        await loadConfig()
      } else {
        showToast(res.data?.error || '保存失败', 'error')
      }
    }
  } catch {
    showToast('保存配置失败', 'error')
  } finally {
    saving.value = false
  }
}

async function loadBackups() {
  if (!decodedPath.value) return
  
  backupsLoading.value = true
  try {
    const res = await getConfigBackups(decodedPath.value)
    if (res.success && res.data?.success) {
      backups.value = res.data.backups
    }
  } catch {
    showToast('加载备份列表失败', 'error')
  } finally {
    backupsLoading.value = false
  }
}

async function restoreBackup(backupName: string) {
  if (!decodedPath.value) return
  
  if (!confirm(`确定要从备份 "${backupName}" 恢复配置吗？当前配置将被覆盖。`)) {
    return
  }
  
  restoringBackup.value = backupName
  try {
    const res = await restoreConfigBackup(decodedPath.value, backupName)
    if (res.success && res.data?.success) {
      showToast('配置已恢复', 'success')
      showBackupsModal.value = false
      await loadConfig()
    } else {
      showToast(res.data?.error || '恢复失败', 'error')
    }
  } catch {
    showToast('恢复备份失败', 'error')
  } finally {
    restoringBackup.value = ''
  }
}

function showToast(message: string, type: 'success' | 'error') {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

watch(showBackupsModal, (show) => {
  if (show) {
    loadBackups()
  }
})

onMounted(() => {
  loadConfig()
  isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
})
</script>

<style scoped>
.plugin-config-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinning {
  animation: spin 1s linear infinite;
}

/* 顶部操作栏 */
.config-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.back-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.header-icon {
  font-size: 32px;
  color: #10b981;
}

.header-info h1 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.header-info p {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.editor-tabs {
  display: flex;
  background: var(--bg-secondary);
  border-radius: var(--radius);
  padding: 4px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: var(--radius);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--bg-primary);
  color: var(--primary);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
}

.btn-ghost:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-dark);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 可视化编辑器 */
.visual-editor {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
}

/* 配置导航栏 */
.config-nav-bar {
  display: flex;
  align-items: center;
  padding: 8px 24px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.nav-tabs {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.nav-tab {
  padding: 10px 20px;
  background: transparent;
  border: none;
  border-radius: var(--radius);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.nav-tab:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-tab.active {
  background: var(--primary-bg);
  color: var(--primary);
}

/* 配置内容 */
.config-content {
  flex: 1;
  overflow: auto;
  padding: 24px;
}

.config-section {
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
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.field-count {
  font-size: 12px;
  color: var(--text-tertiary);
}

.fields-list {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-card {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius);
  border: 1px solid var(--border-color);
}

.field-card.inline {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.field-left {
  flex: 1;
}

.field-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.field-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.field-type {
  font-size: 11px;
  padding: 2px 6px;
  background: var(--bg-primary);
  border-radius: 4px;
  color: var(--text-tertiary);
}

.field-description {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 12px;
}

.field-card.inline .field-description {
  margin-bottom: 0;
}

.field-input {
  margin-top: 12px;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
  flex-shrink: 0;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-hover);
  transition: var(--transition-fast);
  border-radius: 26px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: var(--transition-fast);
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.toggle-switch input:checked + .toggle-slider {
  background-color: var(--primary);
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(22px);
}

/* 源码编辑器 */
.source-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.source-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.file-path {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.monaco-container {
  flex: 1;
  overflow: hidden;
}

.validation-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border-top: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  font-size: 13px;
}

/* 状态提示 */
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px 20px;
  color: var(--text-tertiary);
  font-size: 14px;
}

.loading-state svg,
.error-state svg,
.empty-state svg {
  font-size: 48px;
  opacity: 0.5;
}

.error-state {
  color: #ef4444;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
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
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
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
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.backup-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.backup-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: var(--radius);
}

.backup-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.backup-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.backup-meta {
  font-size: 12px;
  color: var(--text-tertiary);
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--bg-primary);
  border-radius: var(--radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-size: 14px;
  z-index: 2000;
  animation: slideIn 0.3s ease;
}

.toast.success {
  border-left: 4px solid #10b981;
  color: #10b981;
}

.toast.error {
  border-left: 4px solid #ef4444;
  color: #ef4444;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
