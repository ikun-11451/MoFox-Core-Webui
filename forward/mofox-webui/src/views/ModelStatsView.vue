<template>
  <div class="model-stats-view">
    <div class="view-header">
      <div class="header-content">
        <h2>模型统计</h2>
        <p class="subtitle">查看各模型的详细使用情况和 Token 消耗</p>
      </div>
      <div class="header-actions">
        <button class="m3-button filled" @click="fetchData" :disabled="loading">
          <span class="material-symbols-rounded icon" :class="{ spinning: loading }">refresh</span>
          刷新数据
        </button>
      </div>
    </div>

    <div class="stats-content">
      <div v-if="loading && !statsData" class="loading-state">
        <span class="material-symbols-rounded spinning">refresh</span>
        加载中...
      </div>
      
      <div v-else-if="statsData && Object.keys(statsData).length > 0" class="stats-grid">
        <div 
          v-for="(stats, model) in statsData" 
          :key="model" 
          class="m3-card model-card"
          @click="openDetail(model, stats)"
        >
          <div class="card-header">
            <div class="model-info">
              <span class="material-symbols-rounded model-icon">psychology</span>
              <h3 class="model-name" :title="model">{{ model }}</h3>
            </div>
          </div>
          
          <div class="card-body">
            <div class="stat-row">
              <div class="stat-item">
                <span class="label">提示词 (Prompt)</span>
                <span class="value">{{ stats.prompt_tokens }}</span>
              </div>
              <div class="stat-item" style="text-align: right;">
                <span class="label">生成 (Completion)</span>
                <span class="value">{{ stats.completion_tokens }}</span>
              </div>
            </div>
            
            <div class="stat-divider"></div>
            
            <div class="stat-row total-row">
              <div class="stat-item">
                <span class="label">总计 Token</span>
                <span class="value highlight">{{ stats.total_tokens }}</span>
              </div>
              <div class="stat-item" style="text-align: right;">
                <span class="label">调用次数</span>
                <span class="value">{{ stats.total_calls }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <span class="material-symbols-rounded empty-icon">data_usage</span>
        <h3>暂无数据</h3>
        <p>还没有产生任何模型调用记录</p>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div class="m3-dialog-overlay" v-if="selectedModel" @click="closeDetail">
      <div class="m3-dialog" :class="{ 'has-tasks': getTasksForModel(selectedModel.name).length > 0 }" @click.stop>
        <div class="dialog-header">
          <h3>模型详情</h3>
          <button class="m3-icon-button" @click="closeDetail">
            <span class="material-symbols-rounded">close</span>
          </button>
        </div>
        <div class="dialog-content">
          <div class="detail-header">
            <span class="material-symbols-rounded detail-icon">psychology</span>
            <div class="detail-title">
              <div class="detail-name">{{ selectedModel.name }}</div>
              <div class="detail-badge">{{ selectedModel.stats.total_calls }} 次调用</div>
            </div>
          </div>
          
          <div class="detail-body-layout">
            <div class="stats-section">
              <div class="detail-grid">
                <div class="detail-card filled">
                  <div class="detail-label">总计消耗 (Total)</div>
                  <div class="detail-value">{{ selectedModel.stats.total_tokens }}</div>
                </div>
                <div class="detail-card">
                  <div class="detail-label">提示词 (Prompt)</div>
                  <div class="detail-value">{{ selectedModel.stats.prompt_tokens }}</div>
                </div>
                <div class="detail-card">
                  <div class="detail-label">生成 (Completion)</div>
                  <div class="detail-value">{{ selectedModel.stats.completion_tokens }}</div>
                </div>
                <div class="detail-card">
                  <div class="detail-label">平均消耗 / 次</div>
                  <div class="detail-value">{{ Math.round(selectedModel.stats.total_tokens / (selectedModel.stats.total_calls || 1)) }}</div>
                </div>
              </div>
            </div>

            <div class="tasks-section" v-if="getTasksForModel(selectedModel.name).length > 0">
              <div class="section-title">应用场景</div>
              <div class="tasks-grid">
                <div v-for="task in getTasksForModel(selectedModel.name)" :key="task" class="task-card">
                  <span class="material-symbols-rounded task-icon">check_circle</span>
                  <span class="task-name">{{ task }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getModelUsageStats, getConfigList, getConfigContent, type ConfigFileInfo } from '@/api'
import { showError } from '@/utils/dialog'

const loading = ref(false)
const statsData = ref<Record<string, Record<string, number>> | null>(null)
const selectedModel = ref<{ name: string; stats: any } | null>(null)
const modelTasks = ref<Record<string, string[]>>({})

const fetchData = async () => {
  loading.value = true
  try {
    const [statsRes, configListRes] = await Promise.all([
      getModelUsageStats(),
      getConfigList()
    ])

    if (statsRes.success && statsRes.data) {
      statsData.value = statsRes.data.stats
    } else {
      showError('获取数据失败: ' + (statsRes.error || '未知错误'))
    }

    // 获取模型配置以分析用途
    if (configListRes.success && configListRes.data) {
      // 扫描主配置和模型配置
      const targetConfigs = configListRes.data.configs.filter((c: ConfigFileInfo) => 
        c.type === 'model' || c.type === 'main'
      )
      
      for (const config of targetConfigs) {
        const contentRes = await getConfigContent(config.path)
        if (contentRes.success && contentRes.data && contentRes.data.parsed) {
          analyzeModelTasks(contentRes.data.parsed)
        }
      }
    }
  } catch (e) {
    showError('网络请求失败: ' + e)
  } finally {
    loading.value = false
  }
}

const analyzeModelTasks = (config: Record<string, any>) => {
  const tasks: Record<string, string[]> = { ...modelTasks.value } // 保留已有的任务
  
  // 1. 处理 model_task_config (标准结构)
  if (config.model_task_config && typeof config.model_task_config === 'object') {
    const taskConfig = config.model_task_config as Record<string, any>
    
    // 任务名称映射表
    const taskNameMap: Record<string, string> = {
      'replyer': '主回复 (Replyer)',
      'planner': '规划 (Planner)',
      'emotion': '情感分析 (Emotion)',
      'mood': '心情 (Mood)',
      'maizone': 'MaiZone',
      'tool_use': '工具调用 (Tool Use)',
      'anti_injection': '反注入 (Anti-Injection)',
      'vlm': '视觉识别 (VLM)',
      'emoji_vlm': '表情包识别 (Emoji VLM)',
      'utils_video': '视频处理',
      'voice': '语音 (Voice)',
      'embedding': '向量 (Embedding)',
      'memory_short_term_builder': '短时记忆构建',
      'memory_short_term_decider': '短时记忆决策',
      'memory_long_term_builder': '长时记忆构建',
      'memory_judge': '记忆评判',
      'lpmm_entity_extract': '实体提取',
      'lpmm_rdf_build': '知识图谱构建',
      'lpmm_qa': '知识库问答',
      'schedule_generator': '日程生成',
      'monthly_plan_generator': '月度计划',
      'relationship_tracker': '关系追踪'
    }

    for (const [taskKey, taskSettings] of Object.entries(taskConfig)) {
      if (taskSettings && Array.isArray(taskSettings.model_list)) {
        const modelList = taskSettings.model_list as string[]
        
        let taskName = taskNameMap[taskKey] || (taskKey.charAt(0).toUpperCase() + taskKey.slice(1))

        for (const modelName of modelList) {
          if (!tasks[modelName]) tasks[modelName] = []
          if (!tasks[modelName].includes(taskName)) {
            tasks[modelName].push(taskName)
          }
        }
      }
    }
  }

  // 2. 通用遍历逻辑 (兼容旧格式或其他配置)
  const traverse = (obj: any, path: string[]) => {
    if (typeof obj !== 'object' || obj === null) return
    
    // 跳过 model_task_config，因为上面已经处理过了
    if (path.length === 0 && obj === config.model_task_config) return 
    if (path.includes('model_task_config')) return

    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'string' && (key === 'model' || key.endsWith('_model') || key === 'model_name')) {
        const modelName = value
        if (!tasks[modelName]) tasks[modelName] = []
        
        // 格式化任务名称
        let taskName = path[0] || 'Unknown'
        
        // 常见 Section 映射
        if (taskName === 'llm') taskName = '主回复 (LLM)'
        else if (taskName === 'emoji') taskName = '表情包识别 (Emoji)'
        else if (taskName === 'vision') taskName = '视觉识别 (Vision)'
        else if (taskName === 'embedding') taskName = '文本向量 (Embedding)'
        else if (taskName === 'speech' || taskName === 'tts') taskName = '语音合成 (TTS)'
        else if (taskName === 'stt') taskName = '语音转文字 (STT)'
        else if (taskName === 'translation') taskName = '翻译 (Translation)'
        else if (taskName === 'summary') taskName = '总结 (Summary)'
        
        // 如果是 generic 的 section，加上 key 的提示
        if (!['llm', 'emoji', 'vision', 'embedding', 'speech', 'tts', 'stt', 'translation', 'summary'].includes(path[0])) {
           const sectionName = path[0].charAt(0).toUpperCase() + path[0].slice(1)
           taskName = `${sectionName}`
           if (path.length > 1) {
             taskName += ` (${path.slice(1).join('.')})`
           }
        }

        if (!tasks[modelName].includes(taskName)) {
          tasks[modelName].push(taskName)
        }
      } else if (typeof value === 'object') {
        traverse(value, [...path, key])
      }
    }
  }
  
  traverse(config, [])
  console.log('[ModelStats] Analyzed tasks:', tasks)
  modelTasks.value = tasks
}

const openDetail = (model: string, stats: any) => {
  selectedModel.value = { name: model, stats }
}

const closeDetail = () => {
  selectedModel.value = null
}

const getTasksForModel = (modelName: string) => {
  if (!modelTasks.value) return []
  
  // 1. 精确匹配
  if (modelTasks.value[modelName]) return modelTasks.value[modelName]
  
  // 2. 模糊匹配 (忽略大小写，或者包含关系)
  const lowerModelName = modelName.toLowerCase()
  for (const [key, tasks] of Object.entries(modelTasks.value)) {
    const lowerKey = key.toLowerCase()
    // 如果配置中的名字包含在统计名字中，或者统计名字包含在配置名字中
    // 例如配置: "gemini-pro", 统计: "models/gemini-pro" -> 匹配
    if (lowerModelName.includes(lowerKey) || lowerKey.includes(lowerModelName)) {
      return tasks
    }
  }
  
  return []
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.model-stats-view {
  padding: 24px;
  height: 100%;
  overflow-y: auto;
  box-sizing: border-box;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-content h2 {
  margin: 0;
  font-size: 24px;
  color: var(--md-sys-color-on-surface);
}

.subtitle {
  margin: 4px 0 0;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 14px;
}

.m3-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 24px;
  height: 40px;
  border-radius: 20px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.m3-button.filled {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

.m3-button.filled:hover {
  box-shadow: var(--md-sys-elevation-1);
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.m3-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.model-card {
  background: var(--md-sys-color-surface-container);
  border-radius: 24px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.model-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--md-sys-elevation-2);
  background: var(--md-sys-color-surface-container-high);
}

.card-header {
  padding: 20px 24px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-info {
  display: flex;
  align-items: center;
  gap: 16px;
  overflow: hidden;
}

.model-icon {
  color: var(--md-sys-color-on-secondary-container);
  background: var(--md-sys-color-secondary-container);
  padding: 12px;
  border-radius: 50%;
  font-size: 24px;
}

.model-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-body {
  padding: 0 24px 24px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  font-size: 12px;
  color: var(--md-sys-color-on-surface-variant);
}

.value {
  font-size: 18px;
  font-family: 'Noto Sans SC', sans-serif;
  color: var(--md-sys-color-on-surface);
  font-weight: 500;
}

.stat-divider {
  height: 1px;
  background: var(--md-sys-color-outline-variant);
  margin: 16px 0;
  opacity: 0.5;
}

.total-row .value.highlight {
  color: var(--md-sys-color-primary);
  font-weight: 700;
  font-size: 24px;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--md-sys-color-on-surface-variant);
  gap: 16px;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 64px;
  opacity: 0.5;
}

/* Dialog Styles */
.m3-dialog-overlay {
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

.m3-dialog {
  background: var(--md-sys-color-surface-container);
  width: 90%;
  max-width: 500px;
  border-radius: 28px;
  display: flex;
  flex-direction: column;
  box-shadow: var(--md-sys-elevation-3);
  animation: dialogIn 0.3s cubic-bezier(0.2, 0, 0, 1);
  transition: max-width 0.3s cubic-bezier(0.2, 0, 0, 1);
}

.m3-dialog.has-tasks {
  max-width: 800px;
}

@keyframes dialogIn {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}

.dialog-header {
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.dialog-header h3 {
  margin: 0;
  font-size: 22px;
  color: var(--md-sys-color-on-surface);
}

.m3-icon-button {
  background: transparent;
  border: none;
  color: var(--md-sys-color-on-surface-variant);
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.m3-icon-button:hover {
  background: var(--md-sys-color-surface-container-highest);
}

.dialog-content {
  padding: 24px;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
}

.detail-icon {
  font-size: 32px;
  color: var(--md-sys-color-primary);
  background: var(--md-sys-color-surface-container-high);
  padding: 12px;
  border-radius: 16px;
}

.detail-title {
  flex: 1;
}

.detail-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 8px;
  word-break: break-all;
  line-height: 1.4;
}

.detail-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.task-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-badge {
  display: inline-block;
  padding: 4px 12px;
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
}

.task-badge {
  display: inline-block;
  padding: 4px 12px;
  background: var(--md-sys-color-tertiary-container);
  color: var(--md-sys-color-on-tertiary-container);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.detail-card {
  background: var(--md-sys-color-surface-container-low);
  padding: 16px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-card.filled {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  grid-column: span 2;
}

.detail-card.filled .detail-label {
  color: var(--md-sys-color-on-primary-container);
  opacity: 0.8;
}

.detail-card.filled .detail-value {
  color: var(--md-sys-color-on-primary-container);
}

.detail-label {
  font-size: 12px;
  color: var(--md-sys-color-on-surface-variant);
}

.detail-value {
  font-size: 20px;
  font-family: 'Noto Sans SC', sans-serif;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.detail-body-layout {
  display: flex;
  gap: 24px;
}

.stats-section {
  flex: 1;
  min-width: 300px;
}

.tasks-section {
  flex: 1;
  min-width: 250px;
  border-left: 1px solid var(--md-sys-color-outline-variant);
  padding-left: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.task-card {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  padding: 12px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  transition: transform 0.2s;
}

.task-card:hover {
  transform: translateY(-2px);
}

.task-icon {
  font-size: 18px;
  opacity: 0.8;
}

.task-name {
  line-height: 1.2;
}

@media (max-width: 768px) {
  .detail-body-layout {
    flex-direction: column;
  }
  
  .tasks-section {
    border-left: none;
    border-top: 1px solid var(--md-sys-color-outline-variant);
    padding-left: 0;
    padding-top: 24px;
  }
}
</style>
