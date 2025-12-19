<template>
  <div class="plugin-config-view">
    <!-- 顶部操作栏 -->
    <header class="config-header">
      <div class="header-left">
        <button class="m3-icon-button" @click="goBack">
          <span class="material-symbols-rounded">arrow_back</span>
        </button>
        <div class="header-icon-container">
          <span class="material-symbols-rounded header-icon">settings_applications</span>
        </div>
        <div class="header-info">
          <h1>{{ pluginDisplayName || '配置编辑器' }}</h1>
          <p>{{ getShortPath(decodedPath) }}</p>
        </div>
      </div>
      <div class="header-actions">
        <div class="m3-segmented-button">
          <button 
            :class="['segment', { active: editorMode === 'visual' }]"
            @click="editorMode = 'visual'"
          >
            <span class="material-symbols-rounded">grid_view</span>
            可视化
          </button>
          <button 
            :class="['segment', { active: editorMode === 'source' }]"
            @click="editorMode = 'source'"
          >
            <span class="material-symbols-rounded">code</span>
            源码
          </button>
        </div>
        <button class="m3-icon-button" @click="showBackupsModal = true" title="备份历史">
          <span class="material-symbols-rounded">history</span>
        </button>
        <button 
          class="m3-button filled" 
          @click="saveCurrentConfig" 
          :disabled="saving || !hasChanges"
        >
          <span class="material-symbols-rounded" :class="{ spinning: saving }">
            {{ saving ? 'progress_activity' : 'save' }}
          </span>
          {{ saving ? '保存中...' : '保存配置' }}
        </button>
      </div>
    </header>

    <!-- 可视化编辑模式 -->
    <div v-if="editorMode === 'visual'" class="visual-editor">
      <div v-if="loading" class="loading-state">
        <span class="material-symbols-rounded spinning">progress_activity</span>
        加载配置中...
      </div>
      <div v-else-if="loadError" class="error-state">
        <span class="material-symbols-rounded">error</span>
        {{ loadError }}
        <button class="m3-button tonal" @click="loadConfig">重试</button>
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
                class="m3-card field-card"
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
                  <label class="m3-switch">
                    <input 
                      type="checkbox" 
                      :checked="Boolean(editedValues[field.full_key])"
                      @change="(e: any) => updateFieldValue(field.full_key, e.target.checked)"
                    >
                    <span class="m3-switch-track">
                      <span class="m3-switch-thumb"></span>
                    </span>
                  </label>
                </template>

                <!-- 其他类型 -->
                <template v-else>
                  <div class="field-header">
                    <span class="field-name">{{ field.key }}</span>
                    <span class="field-type-badge">{{ field.type }}</span>
                  </div>
                  <div v-if="field.description" class="field-description">
                    {{ field.description }}
                  </div>
                  
                  <!-- 数组/列表类型 -->
                  <div v-if="field.type === 'list' || field.type === 'array'" class="field-input-container">
                    <div class="array-input-wrapper">
                      <textarea
                        class="m3-input array-textarea"
                        :value="formatArrayValue(editedValues[field.full_key])"
                        @input="(e: any) => updateArrayValue(field.full_key, e.target.value)"
                        placeholder="每行一个值"
                      ></textarea>
                      <div class="input-hint">每行输入一个值</div>
                    </div>
                  </div>

                  <!-- 数字类型 -->
                  <div v-else-if="field.type === 'integer' || field.type === 'float' || field.type === 'number'" class="field-input-container">
                    <input 
                      type="number"
                      class="m3-input"
                      :value="editedValues[field.full_key]"
                      @input="(e: any) => updateFieldValue(field.full_key, Number(e.target.value))"
                      :step="field.type === 'float' || field.type === 'number' ? '0.1' : '1'"
                    >
                  </div>

                  <!-- 对象/复杂类型 -->
                  <div v-else-if="field.type === 'object' || field.type === 'array_of_objects'" class="field-input-container">
                    <div class="complex-type-wrapper">
                      <div class="complex-type-header">
                        <span class="material-symbols-rounded">data_object</span>
                        复杂数据结构 (JSON编辑)
                      </div>
                      <textarea
                        class="m3-input code-textarea"
                        :value="formatJsonValue(editedValues[field.full_key])"
                        @change="(e: any) => updateJsonValue(field.full_key, e.target.value)"
                        placeholder="请输入 JSON 格式"
                      ></textarea>
                    </div>
                  </div>

                  <!-- 字符串/默认类型 -->
                  <div v-else class="field-input-container">
                    <input 
                      type="text"
                      class="m3-input"
                      :value="editedValues[field.full_key]"
                      @input="(e: any) => updateFieldValue(field.full_key, e.target.value)"
                    >
                  </div>
                </template>
              </div>
            </div>
          </div>
          <div v-else class="empty-section-state">
            <span class="material-symbols-rounded">settings</span>
            <p>请选择一个配置节</p>
          </div>
        </div>
      </template>
    </div>

    <!-- 源码编辑模式 (Monaco Editor) -->
    <div v-else class="source-editor">
      <div class="source-toolbar">
        <span class="file-path">
          <span class="material-symbols-rounded">description</span>
          {{ decodedPath }}
        </span>
        <div class="toolbar-actions">
          <button class="m3-button text small" @click="formatSource">
            <span class="material-symbols-rounded">format_align_left</span>
            格式化
          </button>
        </div>
      </div>
      <div class="monaco-container">
        <vue-monaco-editor
          v-model:value="sourceContent"
          :language="'ini'"
          :theme="isDarkMode ? 'vs-dark' : 'vs'"
          :options="monacoOptions"
          @mount="onEditorMount"
        />
      </div>
    </div>

    <!-- 备份管理弹窗 -->
    <div v-if="showBackupsModal" class="m3-dialog-overlay" @click.self="showBackupsModal = false">
      <div class="m3-dialog">
        <div class="dialog-header">
          <h3>
            <span class="material-symbols-rounded">history</span>
            备份管理
          </h3>
          <button class="m3-icon-button" @click="showBackupsModal = false">
            <span class="material-symbols-rounded">close</span>
          </button>
        </div>
        <div class="dialog-content">
          <div v-if="backupsLoading" class="loading-state">
            <span class="material-symbols-rounded spinning">progress_activity</span>
            加载备份列表...
          </div>
          <div v-else-if="backups.length" class="backup-list">
            <div class="backup-item" v-for="backup in backups" :key="backup.path">
              <div class="backup-info">
                <span class="backup-name">{{ backup.name }}</span>
                <span class="backup-meta">{{ backup.created_at }} · {{ formatSize(backup.size) }}</span>
              </div>
              <div class="backup-actions">
                <button class="m3-button text small" @click="restoreBackup(backup)">
                  <span class="material-symbols-rounded">restore</span>
                  还原
                </button>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <span class="material-symbols-rounded empty-icon">history_toggle_off</span>
            <p>暂无备份记录</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast 通知 -->
    <Transition name="toast">
      <div v-if="toast.show" class="m3-snackbar" :class="toast.type">
        <span class="material-symbols-rounded">
          {{ toast.type === 'success' ? 'check_circle' : 'error' }}
        </span>
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'
import { 
  getConfigContent, 
  getConfigSchema,
  saveConfig, 
  updateConfig,
  getConfigBackups, 
  restoreConfigBackup,
  getPluginList
} from '@/api'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()

// 路由参数
const decodedPath = computed(() => decodeURIComponent(route.params.path as string))

// 状态
const editorMode = ref<'visual' | 'source'>('visual')
const loading = ref(false)
const saving = ref(false)
const loadError = ref('')
const pluginDisplayName = ref('')
const activeSection = ref(0)

// 数据
const editedValues = ref<Record<string, any>>({})
const originalValues = ref<Record<string, any>>({})
const sourceContent = ref('')
const originalSource = ref('')
const configSchema = ref<any[]>([])

// 备份
const showBackupsModal = ref(false)
const backupsLoading = ref(false)
const backups = ref<any[]>([])

// Toast
const toast = ref({ show: false, message: '', type: 'success' as 'success' | 'error' })

const isDarkMode = computed(() => themeStore.isDark)

// Monaco 配置
const monacoOptions = {
  minimap: { enabled: false },
  fontSize: 14,
  lineHeight: 24,
  fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
  scrollBeyondLastLine: false,
  automaticLayout: true,
  padding: { top: 16, bottom: 16 }
}

// 当前选中的配置节
const currentSection = computed(() => {
  if (configSchema.value.length > 0 && activeSection.value < configSchema.value.length) {
    return configSchema.value[activeSection.value]
  }
  return null
})

// 是否有变更
const hasChanges = computed(() => {
  if (editorMode.value === 'source') {
    return sourceContent.value !== originalSource.value
  } else {
    return JSON.stringify(editedValues.value) !== JSON.stringify(originalValues.value)
  }
})

// 初始化
onMounted(() => {
  loadConfig()
})

function goBack() {
  router.back()
}

function getShortPath(path: string): string {
  const parts = path.split(/[/\\]/)
  if (parts.length > 3) {
    return '...' + parts.slice(-3).join('/')
  }
  return path
}

// 加载配置
async function loadConfig() {
  loading.value = true
  loadError.value = ''
  
  try {
    // 1. 获取配置结构 (Schema)
    const schemaRes = await getConfigSchema(decodedPath.value)
    if (schemaRes.success) {
      configSchema.value = schemaRes.sections
      
      // 初始化编辑值
      const values: Record<string, any> = {}
      schemaRes.sections.forEach((section: any) => {
        section.fields.forEach((field: any) => {
           values[field.full_key] = field.value
        })
      })
      editedValues.value = values
      originalValues.value = JSON.parse(JSON.stringify(values))
    } else {
      throw new Error(schemaRes.error || '获取配置结构失败')
    }

    // 2. 获取原始内容 (Source)
    const contentRes = await getConfigContent(decodedPath.value)
    if (contentRes.success) {
      sourceContent.value = contentRes.content || ''
      originalSource.value = contentRes.content || ''
    }

    // 3. 获取插件信息 (Display Name)
    await fetchPluginInfo()

  } catch (e: any) {
    console.error('加载配置失败:', e)
    loadError.value = e.message || '加载配置失败'
  } finally {
    loading.value = false
  }
}

async function fetchPluginInfo() {
  try {
    // 简单的路径匹配逻辑
    const path = decodedPath.value
    if (path === 'bot_config.toml') {
      pluginDisplayName.value = '机器人主配置'
      return
    }
    if (path === 'model_config.toml') {
      pluginDisplayName.value = '模型配置'
      return
    }

    // 尝试从插件列表匹配
    const pluginsRes = await getPluginList()
    if (pluginsRes.success) {
      const pathParts = path.split('/')
      // 假设路径格式为 plugins/plugin_name/config.toml
      if (pathParts[0] === 'plugins' && pathParts.length >= 2) {
        const pluginDirName = pathParts[1]
        const plugin = pluginsRes.plugins.find(p => p.name === pluginDirName)
        if (plugin) {
          pluginDisplayName.value = plugin.display_name
        } else {
          // 尝试美化文件夹名
          pluginDisplayName.value = pluginDirName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
        }
      }
    }
  } catch (e) {
    console.warn('获取插件信息失败:', e)
  }
}

// 更新字段值
function updateFieldValue(fullKey: string, value: any) {
  editedValues.value[fullKey] = value
}

// 数组值处理
function formatArrayValue(val: any): string {
  if (Array.isArray(val)) return val.join('\n')
  return String(val || '')
}

function updateArrayValue(fullKey: string, val: string) {
  const arr = val.split('\n').map(s => s.trim()).filter(s => s)
  // 尝试转换数字
  const typedArr = arr.map(item => {
    const num = Number(item)
    return isNaN(num) ? item : num
  })
  updateFieldValue(fullKey, typedArr)
}

// JSON 值处理
function formatJsonValue(val: any): string {
  try {
    return JSON.stringify(val, null, 2)
  } catch (e) {
    return String(val)
  }
}

function updateJsonValue(fullKey: string, val: string) {
  try {
    const parsed = JSON.parse(val)
    updateFieldValue(fullKey, parsed)
  } catch (e) {
    // JSON 格式错误时不更新值，或者可以提示错误
    console.warn('JSON 解析失败:', e)
  }
}

// 保存配置
async function saveCurrentConfig() {
  saving.value = true
  try {
    let res
    if (editorMode.value === 'source') {
      res = await saveConfig(decodedPath.value, sourceContent.value)
    } else {
      // 计算变更
      const updates: Record<string, any> = {}
      for (const key in editedValues.value) {
        if (JSON.stringify(editedValues.value[key]) !== JSON.stringify(originalValues.value[key])) {
          updates[key] = editedValues.value[key]
        }
      }
      
      if (Object.keys(updates).length === 0) {
        showToast('没有检测到变更', 'success')
        saving.value = false
        return
      }

      res = await updateConfig(decodedPath.value, updates)
    }

    if (res.success) {
      showToast('配置已保存', 'success')
      // 重新加载以同步状态
      await loadConfig()
    } else {
      showToast(res.error || '保存失败', 'error')
    }
  } catch (e) {
    showToast('保存请求失败', 'error')
  } finally {
    saving.value = false
  }
}

function formatSource() {
  // 简单的格式化 (如果需要更复杂的可以使用 prettier)
  // 这里暂时不做处理，因为 Monaco Editor 内部有格式化功能，或者后端保存时会处理
}

function onEditorMount(editor: any) {
  // 可以在这里添加快捷键等
}

// 备份相关
watch(showBackupsModal, (val) => {
  if (val) fetchBackups()
})

async function fetchBackups() {
  backupsLoading.value = true
  try {
    const res = await getConfigBackups(decodedPath.value)
    if (res.success && res.backups) {
      backups.value = res.backups
    }
  } catch (e) {
    console.error(e)
  } finally {
    backupsLoading.value = false
  }
}

async function restoreBackup(backup: any) {
  if (!confirm(`确定要还原到 ${backup.created_at} 的版本吗？`)) return
  try {
    const res = await restoreConfigBackup(decodedPath.value, backup.name)
    if (res.success) {
      showToast('还原成功', 'success')
      showBackupsModal.value = false
      await loadConfig()
    } else {
      showToast(res.error || '还原失败', 'error')
    }
  } catch (e) {
    showToast('还原请求失败', 'error')
  }
}

// 工具函数
function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  return (bytes / 1024).toFixed(1) + ' KB'
}

function showToast(msg: string, type: 'success' | 'error' = 'success') {
  toast.value = { show: true, message: msg, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}
</script>

<style scoped>
.plugin-config-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
  animation: fadeIn 0.4s cubic-bezier(0.2, 0, 0, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 头部样式 */
.config-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  background: var(--md-sys-color-surface-container);
  border-radius: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon-container {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon {
  font-size: 24px;
}

.header-info h1 {
  font-size: 22px;
  font-weight: 400;
  color: var(--md-sys-color-on-surface);
  margin: 0 0 4px;
}

.header-info p {
  font-size: 14px;
  color: var(--md-sys-color-on-surface-variant);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 分段按钮 */
.m3-segmented-button {
  display: flex;
  border: 1px solid var(--md-sys-color-outline);
  border-radius: 20px;
  overflow: hidden;
  height: 40px;
}

.segment {
  background: transparent;
  border: none;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
  cursor: pointer;
  transition: all 0.2s;
  border-right: 1px solid var(--md-sys-color-outline);
}

.segment:last-child {
  border-right: none;
}

.segment:hover {
  background: var(--md-sys-color-surface-container-highest);
}

.segment.active {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}

.segment .material-symbols-rounded {
  font-size: 18px;
}

/* 编辑器区域 */
.visual-editor, .source-editor {
  flex: 1;
  background: var(--md-sys-color-surface-container-low);
  border-radius: 24px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.visual-editor {
  display: flex;
  flex-direction: column;
}

.config-nav-bar {
  padding: 16px 24px 0;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface-container);
}

.nav-tabs {
  display: flex;
  gap: 24px;
  overflow-x: auto;
}

.nav-tab {
  background: transparent;
  border: none;
  padding: 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
  cursor: pointer;
  position: relative;
  white-space: nowrap;
}

.nav-tab.active {
  color: var(--md-sys-color-primary);
}

.nav-tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--md-sys-color-primary);
  border-radius: 3px 3px 0 0;
}

.config-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
  margin: 0;
}

.field-count {
  font-size: 12px;
  color: var(--md-sys-color-on-surface-variant);
  background: var(--md-sys-color-surface-container-highest);
  padding: 2px 8px;
  border-radius: 100px;
}

.fields-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-card {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-card.inline {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.field-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.field-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
}

.field-type-badge {
  font-size: 11px;
  color: var(--md-sys-color-on-surface-variant);
  background: var(--md-sys-color-surface-container-highest);
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.field-description {
  font-size: 12px;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.4;
  white-space: pre-wrap;
}

.field-input-container {
  width: 100%;
}

.array-textarea {
  height: 100px;
  padding: 12px;
  font-family: monospace;
  resize: vertical;
}

.code-textarea {
  height: 150px;
  padding: 12px;
  font-family: 'JetBrains Mono', monospace;
  resize: vertical;
  font-size: 13px;
}

.complex-type-wrapper {
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 8px;
  overflow: hidden;
}

.complex-type-header {
  padding: 8px 12px;
  background: var(--md-sys-color-surface-container-highest);
  font-size: 12px;
  color: var(--md-sys-color-on-surface-variant);
  display: flex;
  align-items: center;
  gap: 8px;
}

.complex-type-header .material-symbols-rounded {
  font-size: 16px;
}

.input-hint {
  font-size: 11px;
  color: var(--md-sys-color-on-surface-variant);
  margin-top: 4px;
}

/* 源码编辑器 */
.source-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: var(--md-sys-color-surface-container);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.file-path {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--md-sys-color-on-surface-variant);
  font-family: monospace;
}

.monaco-container {
  flex: 1;
  min-height: 0;
}

/* 状态展示 */
.loading-state, .error-state, .empty-state, .empty-section-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: var(--md-sys-color-on-surface-variant);
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 备份列表 */
.backup-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.backup-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--md-sys-color-surface-container-highest);
  border-radius: 12px;
}

.backup-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
  display: block;
}

.backup-meta {
  font-size: 12px;
  color: var(--md-sys-color-on-surface-variant);
}

/* Snackbar */
.m3-snackbar {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--md-sys-color-inverse-surface);
  color: var(--md-sys-color-inverse-on-surface);
  padding: 14px 24px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: var(--md-sys-elevation-3);
  z-index: 2000;
  min-width: 300px;
}

.m3-snackbar.error {
  background: var(--md-sys-color-error-container);
  color: var(--md-sys-color-on-error-container);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, 20px);
}
</style>
