<template>
  <div class="config-manager">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <Icon icon="lucide:settings-2" />
          配置管理
        </h1>
        <p class="page-desc">可视化编辑和管理所有配置文件</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="refreshConfigList" :disabled="loading">
          <Icon icon="lucide:refresh-cw" :class="{ spinning: loading }" />
          刷新
        </button>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 配置文件列表侧边栏 -->
      <aside class="config-sidebar">
        <div class="sidebar-header">
          <h3>配置文件</h3>
          <span class="config-count">{{ configList.length }} 个</span>
        </div>
        
        <!-- 分类标签 -->
        <div class="category-tabs">
          <button 
            v-for="cat in categories" 
            :key="cat.type"
            :class="['category-tab', { active: activeCategory === cat.type }]"
            @click="activeCategory = cat.type"
          >
            <Icon :icon="cat.icon" />
            {{ cat.label }}
            <span class="count">{{ getConfigsByCategory(cat.type).length }}</span>
          </button>
        </div>

        <!-- 配置文件列表 -->
        <div class="config-list">
          <div v-if="loading" class="loading-state">
            <Icon icon="lucide:loader-2" class="spinning" />
            加载中...
          </div>
          <div v-else-if="filteredConfigs.length === 0" class="empty-state">
            <Icon icon="lucide:file-x" />
            暂无配置文件
          </div>
          <div 
            v-else
            v-for="config in filteredConfigs" 
            :key="config.path"
            :class="['config-item', { active: selectedConfig?.path === config.path }]"
            @click="selectConfig(config)"
          >
            <div class="config-item-icon">
              <Icon :icon="getConfigIcon(config.type)" />
            </div>
            <div class="config-item-info">
              <span class="config-name">{{ config.display_name }}</span>
              <span class="config-path">{{ config.path }}</span>
            </div>
            <div class="config-item-time" v-if="config.last_modified">
              {{ formatTime(config.last_modified) }}
            </div>
          </div>
        </div>
      </aside>

      <!-- 配置编辑区 -->
      <main class="config-editor">
        <div v-if="!selectedConfig" class="no-selection">
          <Icon icon="lucide:file-cog" />
          <p>请从左侧选择一个配置文件</p>
        </div>
        
        <template v-else>
          <!-- 编辑器头部 -->
          <div class="editor-header">
            <div class="editor-title">
              <Icon :icon="getConfigIcon(selectedConfig.type)" />
              <h2>{{ selectedConfig.display_name }}</h2>
              <span class="config-type-badge" :class="selectedConfig.type">
                {{ getConfigTypeLabel(selectedConfig.type) }}
              </span>
            </div>
            <div class="editor-tabs">
              <button 
                :class="['tab-btn', { active: editorMode === 'visual' }]"
                @click="editorMode = 'visual'"
              >
                <Icon icon="lucide:layout-grid" />
                可视化编辑
              </button>
              <button 
                :class="['tab-btn', { active: editorMode === 'source' }]"
                @click="editorMode = 'source'"
              >
                <Icon icon="lucide:code" />
                源码编辑
              </button>
            </div>
            <div class="editor-actions">
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
                {{ saving ? '保存中...' : '保存' }}
              </button>
            </div>
          </div>

          <!-- 可视化编辑模式 -->
          <div v-if="editorMode === 'visual'" class="visual-editor">
            <div v-if="schemaLoading" class="loading-state large">
              <Icon icon="lucide:loader-2" class="spinning" />
              加载配置结构...
            </div>
            <div v-else-if="schemaError" class="error-state">
              <Icon icon="lucide:alert-circle" />
              {{ schemaError }}
            </div>
            <div v-else class="sections-container">
              <div 
                v-for="section in configSchema" 
                :key="section.name" 
                class="config-section"
              >
                <div class="section-header" @click="toggleSection(section.name)">
                  <Icon 
                    :icon="expandedSections.includes(section.name) ? 'lucide:chevron-down' : 'lucide:chevron-right'" 
                  />
                  <h3>{{ section.display_name }}</h3>
                  <span class="field-count">{{ section.fields.length }} 项</span>
                </div>
                <div v-show="expandedSections.includes(section.name)" class="section-content">
                  <div 
                    v-for="field in section.fields" 
                    :key="field.full_key" 
                    class="field-row"
                  >
                    <div class="field-label">
                      <span class="field-name">{{ field.key }}</span>
                      <span v-if="field.description" class="field-desc" :title="field.description">
                        <Icon icon="lucide:info" />
                      </span>
                    </div>
                    <div class="field-input">
                      <!-- 布尔值 -->
                      <label v-if="field.type === 'boolean'" class="toggle-switch">
                        <input 
                          type="checkbox" 
                          :checked="getFieldValueAsBoolean(field.full_key)"
                          @change="updateFieldValue(field.full_key, ($event.target as HTMLInputElement).checked)"
                        />
                        <span class="toggle-slider"></span>
                        <span class="toggle-label">{{ getFieldValueAsBoolean(field.full_key) ? '启用' : '禁用' }}</span>
                      </label>
                      <!-- 数字 -->
                      <input 
                        v-else-if="field.type === 'integer' || field.type === 'number'"
                        type="number"
                        class="input"
                        :value="getFieldValue(field.full_key)"
                        @input="updateFieldValue(field.full_key, parseNumber(($event.target as HTMLInputElement).value, field.type))"
                      />
                      <!-- 数组 -->
                      <div v-else-if="field.type === 'array'" class="array-editor">
                        <div class="array-preview" @click="openArrayEditor(field)">
                          <span class="array-count">{{ (getFieldValue(field.full_key) as unknown[])?.length || 0 }} 项</span>
                          <Icon icon="lucide:edit-3" />
                        </div>
                      </div>
                      <!-- 对象数组 -->
                      <div v-else-if="field.type === 'array_of_objects'" class="object-array-editor">
                        <div class="array-preview" @click="openObjectArrayEditor(field)">
                          <span class="array-count">{{ field.items_count || 0 }} 个配置项</span>
                          <Icon icon="lucide:edit-3" />
                        </div>
                      </div>
                      <!-- 对象 -->
                      <div v-else-if="field.type === 'object'" class="object-editor">
                        <button class="btn btn-sm btn-ghost" @click="openObjectEditor(field)">
                          <Icon icon="lucide:edit-3" />
                          编辑对象
                        </button>
                      </div>
                      <!-- 字符串（默认） -->
                      <input 
                        v-else
                        type="text"
                        class="input"
                        :value="getFieldValue(field.full_key)"
                        @input="updateFieldValue(field.full_key, ($event.target as HTMLInputElement).value)"
                      />
                    </div>
                    <div v-if="field.description" class="field-description">
                      {{ field.description }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 源码编辑模式 -->
          <div v-else class="source-editor">
            <div class="source-toolbar">
              <span class="file-path">{{ selectedConfig.path }}</span>
              <div class="toolbar-actions">
                <button class="btn btn-sm btn-ghost" @click="formatToml">
                  <Icon icon="lucide:align-left" />
                  格式化
                </button>
                <button class="btn btn-sm btn-ghost" @click="validateCurrentToml">
                  <Icon icon="lucide:check-circle" />
                  验证
                </button>
              </div>
            </div>
            <div class="code-editor-container">
              <textarea 
                ref="codeEditor"
                v-model="sourceContent"
                class="code-editor"
                spellcheck="false"
                @input="onSourceChange"
              ></textarea>
              <div v-if="validationError" class="validation-error">
                <Icon icon="lucide:alert-triangle" />
                {{ validationError }}
              </div>
            </div>
          </div>
        </template>
      </main>
    </div>

    <!-- 备份管理弹窗 -->
    <div v-if="showBackupsModal" class="modal-overlay" @click.self="showBackupsModal = false">
      <div class="modal-content modal-medium">
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
          <div v-else-if="backups.length === 0" class="empty-state small">
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

    <!-- 数组编辑弹窗 -->
    <div v-if="showArrayModal" class="modal-overlay" @click.self="showArrayModal = false">
      <div class="modal-content modal-medium">
        <div class="modal-header">
          <h3>
            <Icon icon="lucide:list" />
            编辑数组: {{ editingArrayField?.key }}
          </h3>
          <button class="close-btn" @click="showArrayModal = false">
            <Icon icon="lucide:x" />
          </button>
        </div>
        <div class="modal-body">
          <div class="array-items">
            <div v-for="(item, index) in editingArrayValue" :key="index" class="array-item">
              <input 
                type="text" 
                class="input" 
                :value="typeof item === 'object' ? JSON.stringify(item) : item"
                @input="updateArrayItem(index, ($event.target as HTMLInputElement).value)"
              />
              <button class="btn btn-sm btn-ghost btn-danger" @click="removeArrayItem(index)">
                <Icon icon="lucide:trash-2" />
              </button>
            </div>
          </div>
          <button class="btn btn-sm btn-ghost add-item-btn" @click="addArrayItem">
            <Icon icon="lucide:plus" />
            添加项
          </button>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showArrayModal = false">取消</button>
          <button class="btn btn-primary" @click="saveArrayEdit">保存</button>
        </div>
      </div>
    </div>

    <!-- 对象数组编辑弹窗 -->
    <div v-if="showObjectArrayModal" class="modal-overlay" @click.self="showObjectArrayModal = false">
      <div class="modal-content modal-large">
        <div class="modal-header">
          <h3>
            <Icon icon="lucide:layers" />
            编辑: {{ editingObjectArrayField?.key }}
          </h3>
          <button class="close-btn" @click="showObjectArrayModal = false">
            <Icon icon="lucide:x" />
          </button>
        </div>
        <div class="modal-body">
          <div class="object-array-tabs">
            <button 
              v-for="(item, index) in editingObjectArrayValue" 
              :key="index"
              :class="['tab-btn', { active: activeObjectIndex === index }]"
              @click="activeObjectIndex = index"
            >
              {{ getObjectLabel(item, index) }}
              <span class="tab-close" @click.stop="removeObjectArrayItem(index)">
                <Icon icon="lucide:x" />
              </span>
            </button>
            <button class="btn btn-sm btn-ghost add-tab-btn" @click="addObjectArrayItem">
              <Icon icon="lucide:plus" />
            </button>
          </div>
          <div v-if="editingObjectArrayValue.length > 0" class="object-fields">
            <div 
              v-for="(value, key) in editingObjectArrayValue[activeObjectIndex]" 
              :key="key" 
              class="field-row"
            >
              <div class="field-label">
                <span class="field-name">{{ key }}</span>
              </div>
              <div class="field-input">
                <input 
                  v-if="typeof value !== 'object' || value === null"
                  type="text"
                  class="input"
                  :value="formatObjectValue(value)"
                  @input="updateObjectField(key as string, ($event.target as HTMLInputElement).value)"
                />
                <textarea 
                  v-else
                  class="input textarea"
                  :value="JSON.stringify(value, null, 2)"
                  @input="updateObjectField(key as string, ($event.target as HTMLInputElement).value, true)"
                ></textarea>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showObjectArrayModal = false">取消</button>
          <button class="btn btn-primary" @click="saveObjectArrayEdit">保存</button>
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
import { ref, computed, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
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
  type ConfigSchemaField,
  type ConfigBackupInfo
} from '@/api'

// 配置分类
const categories = [
  { type: 'all', label: '全部', icon: 'lucide:folder' },
  { type: 'main', label: '主配置', icon: 'lucide:bot' },
  { type: 'model', label: '模型', icon: 'lucide:brain' },
  { type: 'plugin', label: '插件', icon: 'lucide:puzzle' }
]

// 状态
const loading = ref(false)
const saving = ref(false)
const schemaLoading = ref(false)
const backupsLoading = ref(false)
const configList = ref<ConfigFileInfo[]>([])
const selectedConfig = ref<ConfigFileInfo | null>(null)
const activeCategory = ref('all')
const editorMode = ref<'visual' | 'source'>('visual')

// 可视化编辑状态
const configSchema = ref<ConfigSection[]>([])
const expandedSections = ref<string[]>([])
const schemaError = ref('')
const editedValues = ref<Record<string, unknown>>({})
const originalParsed = ref<Record<string, unknown>>({})

// 源码编辑状态
const sourceContent = ref('')
const originalContent = ref('')
const validationError = ref('')

// 备份相关
const showBackupsModal = ref(false)
const backups = ref<ConfigBackupInfo[]>([])
const restoringBackup = ref('')

// 数组编辑相关
const showArrayModal = ref(false)
const editingArrayField = ref<ConfigSchemaField | null>(null)
const editingArrayValue = ref<unknown[]>([])

// 对象数组编辑相关
const showObjectArrayModal = ref(false)
const editingObjectArrayField = ref<ConfigSchemaField | null>(null)
const editingObjectArrayValue = ref<Record<string, unknown>[]>([])
const activeObjectIndex = ref(0)

// Toast 提示
const toast = ref({ show: false, message: '', type: 'success' as 'success' | 'error' })

// 计算属性
const filteredConfigs = computed(() => {
  if (activeCategory.value === 'all') {
    return configList.value
  }
  return configList.value.filter(c => c.type === activeCategory.value)
})

const hasChanges = computed(() => {
  if (editorMode.value === 'source') {
    return sourceContent.value !== originalContent.value
  }
  return Object.keys(editedValues.value).length > 0
})

// 方法
function getConfigsByCategory(type: string): ConfigFileInfo[] {
  if (type === 'all') return configList.value
  return configList.value.filter(c => c.type === type)
}

function getConfigIcon(type: string): string {
  const icons: Record<string, string> = {
    main: 'lucide:bot',
    model: 'lucide:brain',
    plugin: 'lucide:puzzle'
  }
  return icons[type] || 'lucide:file-cog'
}

function getConfigTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    main: '主配置',
    model: '模型配置',
    plugin: '插件配置'
  }
  return labels[type] || '配置'
}

function formatTime(timeStr: string): string {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  return date.toLocaleDateString()
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

async function refreshConfigList() {
  loading.value = true
  try {
    const res = await getConfigList()
    if (res.success && res.data) {
      configList.value = res.data.configs
    }
  } catch (error) {
    showToast('加载配置列表失败', 'error')
  } finally {
    loading.value = false
  }
}

async function selectConfig(config: ConfigFileInfo) {
  if (hasChanges.value) {
    if (!confirm('当前有未保存的更改，确定要切换吗？')) {
      return
    }
  }
  
  selectedConfig.value = config
  editedValues.value = {}
  validationError.value = ''
  
  // 加载内容
  await loadConfigContent(config.path)
  
  // 如果是可视化模式，加载结构
  if (editorMode.value === 'visual') {
    await loadConfigSchema(config.path)
  }
}

async function loadConfigContent(path: string) {
  try {
    const res = await getConfigContent(path)
    if (res.success && res.data) {
      sourceContent.value = res.data.content || ''
      originalContent.value = res.data.content || ''
      originalParsed.value = res.data.parsed || {}
    } else {
      showToast(res.data?.error || '加载配置失败', 'error')
    }
  } catch (error) {
    showToast('加载配置内容失败', 'error')
  }
}

async function loadConfigSchema(path: string) {
  schemaLoading.value = true
  schemaError.value = ''
  
  try {
    const res = await getConfigSchema(path)
    if (res.success && res.data) {
      if (res.data.success) {
        configSchema.value = res.data.sections
        // 默认展开第一个 section
        if (res.data.sections.length > 0 && expandedSections.value.length === 0) {
          const firstSection = res.data.sections[0]
          if (firstSection) {
            expandedSections.value = [firstSection.name]
          }
        }
      } else {
        schemaError.value = res.data.error || '加载配置结构失败'
      }
    }
  } catch (error) {
    schemaError.value = '加载配置结构失败'
  } finally {
    schemaLoading.value = false
  }
}

function toggleSection(sectionName: string) {
  const index = expandedSections.value.indexOf(sectionName)
  if (index >= 0) {
    expandedSections.value.splice(index, 1)
  } else {
    expandedSections.value.push(sectionName)
  }
}

function getFieldValue(fullKey: string): unknown {
  // 优先返回编辑后的值
  if (fullKey in editedValues.value) {
    return editedValues.value[fullKey]
  }
  
  // 否则从原始解析数据中获取
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

function getFieldValueAsBoolean(fullKey: string): boolean {
  const value = getFieldValue(fullKey)
  return Boolean(value)
}

function updateFieldValue(fullKey: string, value: unknown) {
  editedValues.value[fullKey] = value
}

function parseNumber(value: string, type: string): number {
  if (type === 'integer') {
    return parseInt(value) || 0
  }
  return parseFloat(value) || 0
}

function onSourceChange() {
  validationError.value = ''
}

function formatToml() {
  // 简单格式化：移除多余空行
  sourceContent.value = sourceContent.value
    .split('\n')
    .map(line => line.trimEnd())
    .join('\n')
    .replace(/\n{3,}/g, '\n\n')
}

async function validateCurrentToml() {
  // 简单的前端验证
  try {
    // 检查基本语法
    const lines = sourceContent.value.split('\n')
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      if (line && line.trim().startsWith('[') && !line.trim().endsWith(']')) {
        throw new Error(`第 ${i + 1} 行: section 头未闭合`)
      }
    }
    validationError.value = ''
    showToast('TOML 格式有效', 'success')
  } catch (e) {
    validationError.value = (e as Error).message
    showToast('TOML 格式错误', 'error')
  }
}

async function saveCurrentConfig() {
  if (!selectedConfig.value) return
  
  saving.value = true
  try {
    if (editorMode.value === 'source') {
      // 源码模式：直接保存内容
      const res = await saveConfig(selectedConfig.value.path, sourceContent.value)
      if (res.success && res.data?.success) {
        originalContent.value = sourceContent.value
        showToast('配置已保存', 'success')
        // 重新加载解析后的数据
        await loadConfigContent(selectedConfig.value.path)
      } else {
        showToast(res.data?.error || '保存失败', 'error')
      }
    } else {
      // 可视化模式：更新字段
      if (Object.keys(editedValues.value).length === 0) {
        showToast('没有需要保存的更改', 'error')
        return
      }
      
      const res = await updateConfig(selectedConfig.value.path, editedValues.value)
      if (res.success && res.data?.success) {
        editedValues.value = {}
        showToast('配置已保存', 'success')
        // 重新加载数据
        await loadConfigContent(selectedConfig.value.path)
        await loadConfigSchema(selectedConfig.value.path)
      } else {
        showToast(res.data?.error || '保存失败', 'error')
      }
    }
  } catch (error) {
    showToast('保存配置失败', 'error')
  } finally {
    saving.value = false
  }
}

async function loadBackups() {
  if (!selectedConfig.value) return
  
  backupsLoading.value = true
  try {
    const res = await getConfigBackups(selectedConfig.value.path)
    if (res.success && res.data?.success) {
      backups.value = res.data.backups
    }
  } catch (error) {
    showToast('加载备份列表失败', 'error')
  } finally {
    backupsLoading.value = false
  }
}

async function restoreBackup(backupName: string) {
  if (!selectedConfig.value) return
  
  if (!confirm(`确定要从备份 "${backupName}" 恢复配置吗？当前配置将被覆盖。`)) {
    return
  }
  
  restoringBackup.value = backupName
  try {
    const res = await restoreConfigBackup(selectedConfig.value.path, backupName)
    if (res.success && res.data?.success) {
      showToast('配置已恢复', 'success')
      showBackupsModal.value = false
      // 重新加载配置
      await loadConfigContent(selectedConfig.value.path)
      await loadConfigSchema(selectedConfig.value.path)
    } else {
      showToast(res.data?.error || '恢复失败', 'error')
    }
  } catch (error) {
    showToast('恢复备份失败', 'error')
  } finally {
    restoringBackup.value = ''
  }
}

// 数组编辑
function openArrayEditor(field: ConfigSchemaField) {
  editingArrayField.value = field
  const value = getFieldValue(field.full_key)
  editingArrayValue.value = Array.isArray(value) ? [...value] : []
  showArrayModal.value = true
}

function updateArrayItem(index: number, value: string) {
  editingArrayValue.value[index] = value
}

function removeArrayItem(index: number) {
  editingArrayValue.value.splice(index, 1)
}

function addArrayItem() {
  editingArrayValue.value.push('')
}

function saveArrayEdit() {
  if (editingArrayField.value) {
    updateFieldValue(editingArrayField.value.full_key, [...editingArrayValue.value])
  }
  showArrayModal.value = false
}

// 对象数组编辑
function openObjectArrayEditor(field: ConfigSchemaField) {
  editingObjectArrayField.value = field
  const value = getFieldValue(field.full_key)
  editingObjectArrayValue.value = Array.isArray(value) 
    ? value.map(v => ({ ...v as Record<string, unknown> }))
    : []
  activeObjectIndex.value = 0
  showObjectArrayModal.value = true
}

function getObjectLabel(obj: Record<string, unknown>, index: number): string {
  // 尝试获取 name 或其他标识字段
  if (obj.name) return String(obj.name)
  if (obj.model_identifier) return String(obj.model_identifier)
  return `项 ${index + 1}`
}

function formatObjectValue(value: unknown): string {
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  if (Array.isArray(value)) return JSON.stringify(value)
  return String(value)
}

function updateObjectField(key: string, value: string, isJson: boolean = false) {
  if (activeObjectIndex.value >= editingObjectArrayValue.value.length) return
  
  let parsedValue: unknown = value
  
  // 尝试解析为正确的类型
  if (isJson) {
    try {
      parsedValue = JSON.parse(value)
    } catch {
      parsedValue = value
    }
  } else if (value === 'true') {
    parsedValue = true
  } else if (value === 'false') {
    parsedValue = false
  } else if (/^\d+$/.test(value)) {
    parsedValue = parseInt(value)
  } else if (/^\d+\.\d+$/.test(value)) {
    parsedValue = parseFloat(value)
  }
  
  const targetObj = editingObjectArrayValue.value[activeObjectIndex.value]
  if (targetObj) {
    targetObj[key] = parsedValue
  }
}

function addObjectArrayItem() {
  // 复制第一个元素的结构作为模板
  if (editingObjectArrayValue.value.length > 0) {
    const template = { ...editingObjectArrayValue.value[0] }
    // 清空值
    for (const key in template) {
      if (typeof template[key] === 'string') template[key] = ''
      else if (typeof template[key] === 'number') template[key] = 0
      else if (typeof template[key] === 'boolean') template[key] = false
      else if (Array.isArray(template[key])) template[key] = []
    }
    editingObjectArrayValue.value.push(template)
  } else {
    editingObjectArrayValue.value.push({})
  }
  activeObjectIndex.value = editingObjectArrayValue.value.length - 1
}

function removeObjectArrayItem(index: number) {
  if (editingObjectArrayValue.value.length <= 1) {
    showToast('至少需要保留一项', 'error')
    return
  }
  editingObjectArrayValue.value.splice(index, 1)
  if (activeObjectIndex.value >= editingObjectArrayValue.value.length) {
    activeObjectIndex.value = editingObjectArrayValue.value.length - 1
  }
}

function saveObjectArrayEdit() {
  if (editingObjectArrayField.value) {
    updateFieldValue(editingObjectArrayField.value.full_key, [...editingObjectArrayValue.value])
  }
  showObjectArrayModal.value = false
}

function openObjectEditor(field: ConfigSchemaField) {
  // 对于简单对象，可以复用数组编辑的逻辑
  const value = getFieldValue(field.full_key)
  if (typeof value === 'object' && value !== null) {
    editingObjectArrayField.value = field
    editingObjectArrayValue.value = [{ ...value as Record<string, unknown> }]
    activeObjectIndex.value = 0
    showObjectArrayModal.value = true
  }
}

function showToast(message: string, type: 'success' | 'error') {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// 监听编辑模式变化
watch(editorMode, async (newMode) => {
  if (selectedConfig.value) {
    if (newMode === 'visual') {
      await loadConfigSchema(selectedConfig.value.path)
    }
  }
})

// 监听备份弹窗
watch(showBackupsModal, (show) => {
  if (show) {
    loadBackups()
  }
})

onMounted(() => {
  refreshConfigList()
})
</script>

<style scoped>
.config-manager {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinning {
  animation: spin 1s linear infinite;
}

/* 页面头部 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.page-title svg {
  color: var(--primary);
}

.page-desc {
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0;
}

/* 主内容区 */
.main-content {
  display: flex;
  gap: 20px;
  flex: 1;
  min-height: 0;
}

/* 侧边栏 */
.config-sidebar {
  width: 320px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.config-count {
  font-size: 12px;
  color: var(--text-tertiary);
  padding: 2px 8px;
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
}

/* 分类标签 */
.category-tabs {
  display: flex;
  gap: 4px;
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  flex-wrap: wrap;
}

.category-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border: none;
  background: transparent;
  border-radius: var(--radius);
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.category-tab:hover {
  background: var(--bg-secondary);
}

.category-tab.active {
  background: var(--primary-bg);
  color: var(--primary);
}

.category-tab .count {
  font-size: 11px;
  padding: 1px 6px;
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
}

.category-tab.active .count {
  background: rgba(59, 130, 246, 0.2);
}

/* 配置文件列表 */
.config-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.config-item:hover {
  background: var(--bg-secondary);
}

.config-item.active {
  background: var(--primary-bg);
}

.config-item-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border-radius: var(--radius);
  color: var(--text-secondary);
}

.config-item.active .config-item-icon {
  background: var(--primary);
  color: white;
}

.config-item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.config-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.config-path {
  font-size: 11px;
  color: var(--text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.config-item-time {
  font-size: 11px;
  color: var(--text-tertiary);
}

/* 配置编辑区 */
.config-editor {
  flex: 1;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.no-selection {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-tertiary);
}

.no-selection svg {
  font-size: 48px;
  opacity: 0.5;
}

/* 编辑器头部 */
.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  gap: 16px;
}

.editor-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.editor-title svg {
  font-size: 20px;
  color: var(--primary);
}

.editor-title h2 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.config-type-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 3px 8px;
  border-radius: var(--radius-full);
}

.config-type-badge.main {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.config-type-badge.model {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.config-type-badge.plugin {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.editor-tabs {
  display: flex;
  gap: 4px;
  background: var(--bg-secondary);
  padding: 4px;
  border-radius: var(--radius);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--bg-primary);
  color: var(--primary);
  box-shadow: var(--shadow-sm);
}

.editor-actions {
  display: flex;
  gap: 8px;
}

/* 可视化编辑器 */
.visual-editor {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.sections-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.config-section {
  background: var(--bg-secondary);
  border-radius: var(--radius);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.section-header:hover {
  background: var(--bg-hover);
}

.section-header h3 {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.field-count {
  font-size: 12px;
  color: var(--text-tertiary);
}

.section-content {
  padding: 8px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-row {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 12px;
  align-items: start;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-top: 8px;
}

.field-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  word-break: break-all;
}

.field-desc {
  color: var(--text-tertiary);
  cursor: help;
}

.field-input {
  display: flex;
  align-items: center;
}

.field-description {
  grid-column: 2;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: -8px;
}

/* 输入控件 */
.input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  transition: all var(--transition-fast);
}

.input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px var(--primary-bg);
}

.textarea {
  min-height: 80px;
  resize: vertical;
  font-family: 'JetBrains Mono', monospace;
}

/* Toggle 开关 */
.toggle-switch {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  width: 44px;
  height: 24px;
  background: var(--bg-hover);
  border-radius: 12px;
  position: relative;
  transition: background var(--transition-fast);
}

.toggle-slider::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.toggle-switch input:checked + .toggle-slider {
  background: var(--primary);
}

.toggle-switch input:checked + .toggle-slider::after {
  transform: translateX(20px);
}

.toggle-label {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 数组预览 */
.array-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.array-preview:hover {
  border-color: var(--primary);
}

.array-count {
  font-size: 13px;
  color: var(--text-secondary);
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
  padding: 10px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.file-path {
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-tertiary);
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.code-editor-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.code-editor {
  width: 100%;
  height: 100%;
  padding: 16px;
  border: none;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  resize: none;
  outline: none;
  tab-size: 2;
}

.validation-error {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 10px 16px;
  background: rgba(239, 68, 68, 0.1);
  border-top: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
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

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* 弹窗样式 */
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
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  animation: modalIn 0.2s ease;
  display: flex;
  flex-direction: column;
}

.modal-medium {
  max-width: 500px;
}

.modal-large {
  max-width: 800px;
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
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
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
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: var(--radius);
}

.backup-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
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

/* 数组编辑 */
.array-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.array-item {
  display: flex;
  gap: 8px;
}

.array-item .input {
  flex: 1;
}

.add-item-btn {
  width: 100%;
  justify-content: center;
  border: 1px dashed var(--border-color);
}

/* 对象数组编辑 */
.object-array-tabs {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.object-array-tabs .tab-btn {
  position: relative;
  padding-right: 28px;
}

.tab-close {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  opacity: 0;
  transition: all var(--transition-fast);
}

.tab-btn:hover .tab-close {
  opacity: 1;
}

.tab-close:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.add-tab-btn {
  padding: 8px 12px;
}

.object-fields {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 加载和空状态 */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: var(--text-tertiary);
}

.loading-state.large,
.empty-state.small {
  padding: 60px;
}

.error-state {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 20px;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius);
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
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 500;
  box-shadow: var(--shadow-lg);
  animation: toastIn 0.3s ease;
  z-index: 2000;
}

.toast.success {
  background: #10b981;
  color: white;
}

.toast.error {
  background: #ef4444;
  color: white;
}

@keyframes toastIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式 */
@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
  }
  
  .config-sidebar {
    width: 100%;
    max-height: 300px;
  }
  
  .field-row {
    grid-template-columns: 1fr;
  }
  
  .field-label {
    padding-top: 0;
  }
  
  .field-description {
    grid-column: 1;
  }
}

@media (max-width: 640px) {
  .editor-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .editor-tabs {
    width: 100%;
  }
  
  .tab-btn {
    flex: 1;
    justify-content: center;
  }
  
  .editor-actions {
    width: 100%;
  }
  
  .editor-actions .btn {
    flex: 1;
  }
}
</style>
