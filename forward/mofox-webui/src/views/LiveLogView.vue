<template>
  <div class="live-log-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-group">
          <Icon icon="lucide:radio" class="title-icon" />
          <h1 class="page-title">实时日志</h1>
          <div class="status-badge" :class="{ connected: realtimeEnabled }">
            <span class="status-dot"></span>
            <span class="status-text">{{ realtimeEnabled ? '已连接' : '未连接' }}</span>
          </div>
        </div>
        <p class="page-description">实时查看系统日志输出</p>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="content-wrapper">
      <div class="log-container">
        <!-- 工具栏 -->
        <div class="toolbar">
          <div class="toolbar-left">
            <button 
              class="action-button primary" 
              @click="toggleRealtime"
              :disabled="connecting"
            >
              <Icon :icon="realtimeEnabled ? 'lucide:pause' : 'lucide:play'" />
              <span>{{ realtimeEnabled ? '断开连接' : '开始监听' }}</span>
            </button>
            
            <button 
              class="action-button" 
              @click="clearRealtimeLogs"
              :disabled="!realtimeEnabled && realtimeLogs.length === 0"
            >
              <Icon icon="lucide:trash-2" />
              <span>清空日志</span>
            </button>
            
            <div class="separator-line"></div>
            
            <label class="checkbox-label">
              <input type="checkbox" v-model="autoScroll" />
              <span>自动滚动</span>
            </label>
          </div>
          
          <div class="toolbar-right">
            <div class="filter-group">
              <div class="level-filter-dropdown">
                <button class="filter-button" @click="toggleLevelFilter">
                  <Icon icon="lucide:filter" />
                  <span>日志级别 ({{ selectedLevels.length }})</span>
                  <Icon :icon="showLevelFilter ? 'lucide:chevron-up' : 'lucide:chevron-down'" />
                </button>
                <div v-if="showLevelFilter" class="filter-dropdown-menu">
                  <label v-for="level in logLevels" :key="level" class="filter-option">
                    <input 
                      type="checkbox" 
                      :value="level" 
                      v-model="selectedLevels"
                    />
                    <span :class="`level-badge level-${level.toLowerCase()}`">{{ level }}</span>
                  </label>
                </div>
              </div>
              
              <input 
                v-model="searchQuery" 
                type="text" 
                class="search-input"
                placeholder="搜索日志内容..."
              />
            </div>
          </div>
        </div>

        <!-- 统计信息 -->
        <div class="stats-bar">
          <div class="stat-item">
            <span class="stat-label">总数:</span>
            <span class="stat-value">{{ realtimeLogs.length }}</span>
          </div>
          <div class="stat-item" v-if="realtimeLogs.length !== filteredLogs.length">
            <span class="stat-label">已筛选:</span>
            <span class="stat-value">{{ filteredLogs.length }}</span>
          </div>
          <div class="stat-item" v-for="(count, level) in logLevelCounts" :key="level">
            <span class="stat-label">{{ level }}:</span>
            <span class="stat-value" :class="`level-${level.toLowerCase()}`">{{ count }}</span>
          </div>
        </div>

        <!-- 日志内容区域 -->
        <div class="log-content" ref="logContentContainer">
          <div v-if="connecting" class="loading-state">
            <Icon icon="lucide:loader-2" class="loading-icon spinning" />
            <p>正在连接...</p>
          </div>

          <div v-else-if="!realtimeEnabled && realtimeLogs.length === 0" class="empty-state">
            <Icon icon="lucide:radio" class="empty-icon" />
            <p>点击"开始监听"按钮开始接收实时日志</p>
          </div>

          <div v-else-if="filteredLogs.length === 0" class="empty-state">
            <Icon icon="lucide:filter-x" class="empty-icon" />
            <p>没有匹配的日志</p>
            <p style="font-size: 12px; margin-top: 8px;">尝试调整筛选条件或搜索关键词</p>
          </div>

          <div v-else class="log-entries">
            <div 
              v-for="entry in filteredLogs" 
              :key="entry.line_number"
              class="log-entry"
              :class="`level-${entry.level.toLowerCase()}`"
            >
              <div class="entry-header">
                <span class="entry-time">{{ formatTimestamp(entry.timestamp) }}</span>
                <span class="entry-level" :class="`level-${entry.level.toLowerCase()}`">
                  {{ entry.level }}
                </span>
                <span 
                  class="entry-logger" 
                  v-if="entry.alias || entry.logger_name"
                  :style="entry.color ? { color: entry.color } : {}"
                  :title="entry.alias ? entry.logger_name : ''"
                >
                  {{ entry.alias || entry.logger_name }}
                </span>
                <span class="entry-line">#{{ entry.line_number }}</span>
              </div>
              <div class="entry-message" v-html="formatLogMessage(entry.event)"></div>
              <div v-if="entry.extra" class="entry-extra">
                <details>
                  <summary>额外信息</summary>
                  <pre>{{ JSON.stringify(entry.extra, null, 2) }}</pre>
                </details>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { getServerInfo } from '@/api/index'
import type { LogEntry } from '@/api/log_viewer'

// 状态
const realtimeEnabled = ref(false)
const connecting = ref(false)
const realtimeLogs = ref<LogEntry[]>([])
const autoScroll = ref(true)
const websocket = ref<WebSocket | null>(null)
const logContentContainer = ref<HTMLElement | null>(null)

// 筛选
const logLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
const selectedLevels = ref<string[]>(['INFO', 'WARNING', 'ERROR', 'CRITICAL']) // 默认排除 DEBUG
const showLevelFilter = ref(false)
const searchQuery = ref('')

// 切换级别筛选面板
const toggleLevelFilter = () => {
  showLevelFilter.value = !showLevelFilter.value
}

// 点击外部关闭筛选面板
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.level-filter-dropdown')) {
    showLevelFilter.value = false
  }
}

// 过滤后的日志
const filteredLogs = computed(() => {
  let logs = realtimeLogs.value

  // 按级别筛选（多选）
  if (selectedLevels.value.length > 0 && selectedLevels.value.length < logLevels.length) {
    logs = logs.filter(log => selectedLevels.value.includes(log.level))
  }

  // 按关键词搜索
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    logs = logs.filter(log => 
      log.event.toLowerCase().includes(query) ||
      (log.logger_name && log.logger_name.toLowerCase().includes(query)) ||
      (log.alias && log.alias.toLowerCase().includes(query))
    )
  }

  return logs
})

// 统计各级别日志数量（基于所有日志，不是过滤后的）
const logLevelCounts = computed(() => {
  const counts: Record<string, number> = {
    DEBUG: 0,
    INFO: 0,
    WARNING: 0,
    ERROR: 0,
    CRITICAL: 0
  }

  realtimeLogs.value.forEach(log => {
    const level = log.level
    if (level && counts[level] !== undefined) {
      counts[level]++
    }
  })

  return counts
})

// 格式化时间戳
const formatTimestamp = (timestamp: string) => {
  if (!timestamp) return ''
  return timestamp.replace('T', ' ').substring(0, 19)
}

// 格式化日志消息（处理 ANSI 转义序列和 JSON）
const formatLogMessage = (message: string) => {
  console.log('[formatLogMessage] 输入消息:', message, '类型:', typeof message)
  if (!message) return ''
  
  // 尝试解析 JSON 格式的日志（包括 Python 字典格式）
  try {
    // 先尝试直接解析 JSON
    let parsed = null
    try {
      parsed = JSON.parse(message)
      console.log('[formatLogMessage] 标准JSON解析成功:', parsed)
    } catch {
      // 如果失败，尝试将 Python 字典格式转换为 JSON
      // 将单引号替换为双引号（注意：这是简化处理，可能在某些情况下不够完善）
      console.log('[formatLogMessage] 尝试Python字典格式转换')
      const jsonMessage = message
        .replace(/'/g, '"')  // 单引号转双引号
        .replace(/True/g, 'true')  // Python True -> JSON true
        .replace(/False/g, 'false')  // Python False -> JSON false
        .replace(/None/g, 'null')  // Python None -> JSON null
      console.log('[formatLogMessage] 转换后的JSON字符串:', jsonMessage)
      parsed = JSON.parse(jsonMessage)
      console.log('[formatLogMessage] Python字典格式解析成功:', parsed)
    }
    
    if (parsed && typeof parsed === 'object') {
      // 格式化为可读的文本
      const parts: string[] = []
      if (parsed.event) parts.push(parsed.event)
      if (parsed.logger_name && !parsed.alias) parts.push(`[${parsed.logger_name}]`)
      if (parsed.level) parts.push(`[${parsed.level}]`)
      if (parsed.timestamp) parts.push(`[${parsed.timestamp}]`)
      const result = escapeHtml(parts.join(' '))
      console.log('[formatLogMessage] JSON格式化结果:', result)
      return result
    }
  } catch (e) {
    console.log('[formatLogMessage] JSON解析完全失败，继续ANSI处理:', e)
    // 不是 JSON，继续处理
  }
  
  // 处理 ANSI 转义序列
  const ansiRegex = /\x1b\[(\d+)m/g
  const colorMap: Record<string, string> = {
    '30': '#000000', '31': '#e74c3c', '32': '#2ecc71', '33': '#f39c12',
    '34': '#3498db', '35': '#9b59b6', '36': '#1abc9c', '37': '#ecf0f1',
    '90': '#7f8c8d', '91': '#e74c3c', '92': '#2ecc71', '93': '#f39c12',
    '94': '#3498db', '95': '#9b59b6', '96': '#1abc9c', '97': '#ffffff'
  }
  
  let result = ''
  let lastIndex = 0
  let currentColor = ''
  let match: RegExpExecArray | null
  
  while ((match = ansiRegex.exec(message)) !== null) {
    const text = message.substring(lastIndex, match.index)
    if (text) {
      if (currentColor) {
        result += `<span style="color: ${currentColor};">${escapeHtml(text)}</span>`
      } else {
        result += escapeHtml(text)
      }
    }
    
    const code = match[1]
    if (code === '0') {
      currentColor = ''
    } else if (code && colorMap[code]) {
      currentColor = colorMap[code]
    }
    
    lastIndex = ansiRegex.lastIndex
  }
  
  const remainingText = message.substring(lastIndex)
  if (remainingText) {
    if (currentColor) {
      result += `<span style="color: ${currentColor};">${escapeHtml(remainingText)}</span>`
    } else {
      result += escapeHtml(remainingText)
    }
  }
  
  const finalResult = result || escapeHtml(message)
  console.log('[formatLogMessage] ANSI处理最终结果:', finalResult)
  return finalResult
}

// HTML 转义
const escapeHtml = (text: string) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// 切换实时日志
const toggleRealtime = () => {
  if (realtimeEnabled.value) {
    disconnectWebSocket()
  } else {
    connectWebSocket()
  }
}

// 连接 WebSocket
const connectWebSocket = async () => {
  if (connecting.value || realtimeEnabled.value) return

  connecting.value = true
  try {
    // 动态获取服务器信息
    const serverInfo = await getServerInfo()
    const wsUrl = `ws://${serverInfo.host}:${serverInfo.port}/plugins/webui_backend/log_viewer/realtime`
    
    console.log('正在连接WebSocket:', wsUrl)
    websocket.value = new WebSocket(wsUrl)
    
    websocket.value.onopen = () => {
      console.log('WebSocket已连接')
      realtimeEnabled.value = true
      connecting.value = false
    }
    
    websocket.value.onmessage = (event) => {
      try {
        let logEntry: LogEntry | any = JSON.parse(event.data)
        
        // 检查是否是嵌套的 JSON 字符串（后端可能发送的是字符串化的 JSON）
        if (typeof logEntry === 'string') {
          try {
            logEntry = JSON.parse(logEntry)
          } catch {
            // 如果不是 JSON 字符串，创建一个简单的日志对象
            logEntry = {
              timestamp: new Date().toISOString(),
              level: 'INFO',
              logger_name: 'unknown',
              event: String(logEntry),
              line_number: 0,
              file_name: 'realtime'
            }
          }
        }
        
        
        // 添加行号(用于key)
        logEntry.line_number = realtimeLogs.value.length + 1
        logEntry.file_name = 'realtime'
        
        realtimeLogs.value.push(logEntry as LogEntry)
        
        // 限制缓冲区大小
        if (realtimeLogs.value.length > 1000) {
          realtimeLogs.value.shift()
          // 重新编号
          realtimeLogs.value.forEach((log, index) => {
            log.line_number = index + 1
          })
        }
        
        // 自动滚动到底部
        if (autoScroll.value) {
          nextTick(() => {
            scrollToBottom()
          })
        }
      } catch (error) {
        console.error('解析日志消息失败:', error, event.data)
      }
    }
    
    websocket.value.onerror = (error) => {
      console.error('WebSocket错误:', error)
      connecting.value = false
    }
    
    websocket.value.onclose = () => {
      console.log('WebSocket已断开')
      realtimeEnabled.value = false
      connecting.value = false
    }
  } catch (error) {
    console.error('连接WebSocket失败:', error)
    connecting.value = false
  }
}

// 断开 WebSocket
const disconnectWebSocket = () => {
  if (websocket.value) {
    websocket.value.close()
    websocket.value = null
  }
  realtimeEnabled.value = false
  connecting.value = false
}

// 清空日志
const clearRealtimeLogs = () => {
  realtimeLogs.value = []
}

// 滚动到底部
const scrollToBottom = () => {
  if (logContentContainer.value) {
    logContentContainer.value.scrollTop = logContentContainer.value.scrollHeight
  }
}

// 监听自动滚动变化
watch(autoScroll, (newValue) => {
  if (newValue) {
    nextTick(() => {
      scrollToBottom()
    })
  }
})

// 初始化
onMounted(() => {
  // 可以选择自动连接
  // connectWebSocket()
  
  // 添加点击外部关闭筛选面板的监听器
  document.addEventListener('click', handleClickOutside)
})

// 清理
onUnmounted(() => {
  disconnectWebSocket()
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.live-log-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
}

/* 页面标题 */
.page-header {
  background: transparent;
  border-bottom: none;
  padding: 24px 32px;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.title-icon {
  font-size: 28px;
  color: var(--primary);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.status-badge.connected {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgb(34, 197, 94);
  color: rgb(34, 197, 94);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-tertiary);
}

.status-badge.connected .status-dot {
  background: rgb(34, 197, 94);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.page-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* 主内容区 */
.content-wrapper {
  flex: 1;
  overflow: hidden;
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.log-container {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  height: 100%;
  max-height: calc(100vh - 220px);
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

/* 工具栏 */
.toolbar {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  flex-shrink: 0;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}

.action-button:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--primary);
  color: var(--primary);
}

.action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-button.primary {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.action-button.primary:hover:not(:disabled) {
  background: var(--primary-dark);
}

.separator-line {
  width: 1px;
  height: 24px;
  background: var(--border-color);
  margin: 0 4px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  user-select: none;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.filter-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.level-filter-dropdown {
  position: relative;
}

.filter-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition);
  white-space: nowrap;
}

.filter-button:hover {
  background: var(--bg-hover);
  border-color: var(--primary);
}

.filter-dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 1000;
  min-width: 200px;
  padding: 8px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition);
  user-select: none;
}

.filter-option:hover {
  background: var(--bg-hover);
}

.filter-option input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.level-badge {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 11px;
  flex: 1;
}

.level-badge.level-debug { background: #8b8b8b; color: white; }
.level-badge.level-info { background: #3b82f6; color: white; }
.level-badge.level-warning { background: #f59e0b; color: white; }
.level-badge.level-error { background: #ef4444; color: white; }
.level-badge.level-critical { background: #dc2626; color: white; }

.search-input {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  min-width: 200px;
  transition: all var(--transition);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  background: var(--bg-primary);
}

/* 统计栏 */
.stats-bar {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  flex-shrink: 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.stat-label {
  color: var(--text-secondary);
}

.stat-value {
  font-weight: 600;
  color: var(--text-primary);
}

.stat-value.level-debug { color: #8b8b8b; }
.stat-value.level-info { color: #3b82f6; }
.stat-value.level-warning { color: #f59e0b; }
.stat-value.level-error { color: #ef4444; }
.stat-value.level-critical { color: #dc2626; }

/* 日志内容区 */
.log-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px;
  min-height: 0;
}

.log-content::-webkit-scrollbar {
  width: 8px;
}

.log-content::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 4px;
}

.log-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

.log-content::-webkit-scrollbar-thumb:hover {
  background: var(--text-tertiary);
}

.log-entries {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-entry {
  padding: 12px;
  border-radius: var(--radius);
  border-left: 3px solid var(--border-color);
  background: var(--bg-secondary);
  transition: all var(--transition);
  animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.log-entry:hover {
  background: var(--bg-hover);
}

.log-entry.level-debug { border-left-color: #8b8b8b; }
.log-entry.level-info { border-left-color: #3b82f6; }
.log-entry.level-warning { border-left-color: #f59e0b; }
.log-entry.level-error { border-left-color: #ef4444; }
.log-entry.level-critical { border-left-color: #dc2626; }

.entry-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 12px;
  flex-wrap: wrap;
}

.entry-time {
  color: var(--text-tertiary);
  font-family: 'Consolas', 'Monaco', monospace;
}

.entry-level {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 11px;
}

.entry-level.level-debug { background: #8b8b8b; color: white; }
.entry-level.level-info { background: #3b82f6; color: white; }
.entry-level.level-warning { background: #f59e0b; color: white; }
.entry-level.level-error { background: #ef4444; color: white; }
.entry-level.level-critical { background: #dc2626; color: white; }

.entry-logger {
  font-weight: 600;
  color: var(--text-primary);
}

.entry-line {
  color: var(--text-tertiary);
  margin-left: auto;
}

.entry-message {
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  font-family: 'Consolas', 'Monaco', monospace;
}

.entry-extra {
  margin-top: 8px;
  font-size: 12px;
}

.entry-extra details {
  cursor: pointer;
}

.entry-extra summary {
  color: var(--primary);
  user-select: none;
}

.entry-extra pre {
  margin-top: 8px;
  padding: 8px;
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 11px;
  color: var(--text-secondary);
}

/* 空状态 */
.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
  height: 100%;
}

.empty-icon,
.loading-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-state p,
.loading-state p {
  font-size: 14px;
  margin: 0;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 768px) {
  .content-wrapper {
    padding: 16px;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-left,
  .toolbar-right {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .filter-group {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .search-input {
    flex: 1;
    min-width: auto;
  }
}
</style>
