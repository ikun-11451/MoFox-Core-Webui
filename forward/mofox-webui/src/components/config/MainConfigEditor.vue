<template>
  <div class="main-config-editor">
    <!-- 配置概览 -->
    <div class="config-overview">
      <div class="overview-card">
        <div class="overview-icon bot">
          <Icon icon="lucide:bot" />
        </div>
        <div class="overview-info">
          <h4>机器人配置</h4>
          <p>管理机器人的基础设置和行为参数</p>
        </div>
      </div>
    </div>

    <!-- 配置分组 -->
    <div class="config-groups">
      <!-- 基础信息 -->
      <div class="config-group">
        <div class="group-header">
          <div class="group-title">
            <Icon icon="lucide:info" />
            <h3>基础信息</h3>
          </div>
          <span class="group-hint">配置机器人的名称和基本标识</span>
        </div>
        <div class="group-content">
          <div class="field-card">
            <div class="field-header">
              <span class="field-name">机器人名称</span>
              <span class="field-key">bot.name</span>
            </div>
            <div class="field-description">
              机器人在对话中使用的名称，用户可以通过这个名字称呼机器人
            </div>
            <input 
              type="text" 
              class="input"
              :value="getFieldValue('bot.name')"
              @input="emit('update', 'bot.name', ($event.target as HTMLInputElement).value)"
              placeholder="例如: 小助手"
            />
          </div>
          
          <div class="field-card">
            <div class="field-header">
              <span class="field-name">机器人 QQ 号</span>
              <span class="field-key">bot.qq</span>
            </div>
            <div class="field-description">
              机器人登录使用的 QQ 账号，用于消息收发
            </div>
            <input 
              type="text" 
              class="input"
              :value="getFieldValue('bot.qq')"
              @input="emit('update', 'bot.qq', ($event.target as HTMLInputElement).value)"
              placeholder="QQ 号码"
            />
          </div>
        </div>
      </div>

      <!-- 行为设置 -->
      <div class="config-group">
        <div class="group-header">
          <div class="group-title">
            <Icon icon="lucide:activity" />
            <h3>行为设置</h3>
          </div>
          <span class="group-hint">控制机器人的响应行为和触发条件</span>
        </div>
        <div class="group-content">
          <div class="field-card inline">
            <div class="field-left">
              <div class="field-header">
                <span class="field-name">启用机器人</span>
              </div>
              <div class="field-description">
                控制机器人是否响应消息
              </div>
            </div>
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                :checked="Boolean(getFieldValue('bot.enabled'))"
                @change="emit('update', 'bot.enabled', ($event.target as HTMLInputElement).checked)"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
          
          <div class="field-card inline">
            <div class="field-left">
              <div class="field-header">
                <span class="field-name">私聊响应</span>
              </div>
              <div class="field-description">
                是否响应私聊消息
              </div>
            </div>
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                :checked="Boolean(getFieldValue('bot.private_chat'))"
                @change="emit('update', 'bot.private_chat', ($event.target as HTMLInputElement).checked)"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
          
          <div class="field-card inline">
            <div class="field-header">
              <div class="field-left">
                <span class="field-name">群聊响应</span>
              </div>
              <div class="field-description">
                是否响应群聊消息
              </div>
            </div>
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                :checked="Boolean(getFieldValue('bot.group_chat'))"
                @change="emit('update', 'bot.group_chat', ($event.target as HTMLInputElement).checked)"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
          
          <div class="field-card">
            <div class="field-header">
              <span class="field-name">触发词</span>
              <span class="field-key">bot.trigger_words</span>
            </div>
            <div class="field-description">
              用户发送这些词语时会触发机器人响应，多个词语用逗号分隔
            </div>
            <input 
              type="text" 
              class="input"
              :value="formatArrayValue(getFieldValue('bot.trigger_words'))"
              @input="emit('update', 'bot.trigger_words', parseArrayValue(($event.target as HTMLInputElement).value))"
              placeholder="例如: 小助手, @机器人"
            />
          </div>
          
          <div class="field-card">
            <div class="field-header">
              <span class="field-name">响应概率</span>
              <span class="field-key">bot.response_probability</span>
            </div>
            <div class="field-description">
              机器人响应普通消息的概率 (0-100%)，设置为 100 表示总是响应
            </div>
            <div class="slider-input">
              <input 
                type="range" 
                min="0" 
                max="100"
                :value="getFieldValue('bot.response_probability') || 0"
                @input="emit('update', 'bot.response_probability', parseInt(($event.target as HTMLInputElement).value))"
              />
              <span class="slider-value">{{ getFieldValue('bot.response_probability') || 0 }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 消息设置 -->
      <div class="config-group">
        <div class="group-header">
          <div class="group-title">
            <Icon icon="lucide:message-square" />
            <h3>消息设置</h3>
          </div>
          <span class="group-hint">配置消息处理和发送相关参数</span>
        </div>
        <div class="group-content">
          <div class="field-card">
            <div class="field-header">
              <span class="field-name">消息长度限制</span>
              <span class="field-key">message.max_length</span>
            </div>
            <div class="field-description">
              单条消息的最大字符数，超出部分会被截断或分段发送
            </div>
            <input 
              type="number" 
              class="input"
              :value="getFieldValue('message.max_length')"
              @input="emit('update', 'message.max_length', parseInt(($event.target as HTMLInputElement).value))"
              placeholder="默认: 4000"
            />
          </div>
          
          <div class="field-card">
            <div class="field-header">
              <span class="field-name">消息发送延迟</span>
              <span class="field-key">message.send_delay</span>
            </div>
            <div class="field-description">
              连续发送多条消息时的间隔时间（毫秒），避免消息过于密集
            </div>
            <input 
              type="number" 
              class="input"
              :value="getFieldValue('message.send_delay')"
              @input="emit('update', 'message.send_delay', parseInt(($event.target as HTMLInputElement).value))"
              placeholder="默认: 1000"
            />
          </div>
        </div>
      </div>

      <!-- 通用配置区域（显示其他未分类的配置） -->
      <div v-for="section in configSchema" :key="section.name" class="config-group">
        <div class="group-header">
          <div class="group-title">
            <Icon icon="lucide:settings" />
            <h3>{{ section.display_name }}</h3>
          </div>
          <span class="group-hint">{{ section.fields.length }} 项配置</span>
        </div>
        <div class="group-content">
          <div 
            v-for="field in section.fields" 
            :key="field.full_key" 
            class="field-card"
            :class="{ inline: field.type === 'boolean' }"
          >
            <div class="field-left" v-if="field.type === 'boolean'">
              <div class="field-header">
                <span class="field-name">{{ field.key }}</span>
              </div>
              <div v-if="field.description" class="field-description">
                {{ field.description }}
              </div>
            </div>
            <template v-else>
              <div class="field-header">
                <span class="field-name">{{ field.key }}</span>
                <span class="field-key">{{ field.full_key }}</span>
              </div>
              <div v-if="field.description" class="field-description">
                {{ field.description }}
              </div>
            </template>
            
            <div class="field-input" v-if="field.type !== 'boolean'">
              <FieldEditor 
                :field="field"
                :value="getFieldValue(field.full_key)"
                @update="(v) => emit('update', field.full_key, v)"
              />
            </div>
            <label v-else class="toggle-switch">
              <input 
                type="checkbox" 
                :checked="Boolean(getFieldValue(field.full_key))"
                @change="emit('update', field.full_key, ($event.target as HTMLInputElement).checked)"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue'
import type { ConfigSection } from '@/api'
import FieldEditor from './FieldEditor.vue'

const props = defineProps<{
  parsedData: Record<string, unknown>
  editedValues: Record<string, unknown>
  configSchema: ConfigSection[]
}>()

const emit = defineEmits<{
  (e: 'update', key: string, value: unknown): void
}>()

function getFieldValue(fullKey: string): unknown {
  // 优先返回编辑后的值
  if (fullKey in props.editedValues) {
    return props.editedValues[fullKey]
  }
  
  // 否则从原始解析数据中获取
  const keys = fullKey.split('.')
  let current: unknown = props.parsedData
  for (const key of keys) {
    if (current && typeof current === 'object' && key in (current as Record<string, unknown>)) {
      current = (current as Record<string, unknown>)[key]
    } else {
      return undefined
    }
  }
  return current
}

function formatArrayValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return ''
}

function parseArrayValue(value: string): string[] {
  return value.split(',').map(s => s.trim()).filter(s => s)
}
</script>

<style scoped>
.main-config-editor {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 配置概览 */
.config-overview {
  display: flex;
  gap: 16px;
}

.overview-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, var(--primary-bg), rgba(59, 130, 246, 0.2));
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
}

.overview-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius);
  font-size: 28px;
}

.overview-icon.bot {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}

.overview-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.overview-info p {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 0;
}

/* 配置分组 */
.config-groups {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.config-group {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.group-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.group-title svg {
  color: var(--primary);
  font-size: 18px;
}

.group-title h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.group-hint {
  font-size: 12px;
  color: var(--text-tertiary);
}

.group-content {
  padding: 20px;
  display: grid;
  gap: 16px;
}

/* 字段卡片 */
.field-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius);
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}

.field-card:hover {
  border-color: var(--border-color);
}

.field-card.inline {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.field-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.field-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.field-key {
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-tertiary);
  padding: 2px 8px;
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
}

.field-description {
  font-size: 12px;
  color: var(--text-tertiary);
  line-height: 1.5;
}

.field-input {
  margin-top: 4px;
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

/* Toggle 开关 */
.toggle-switch {
  display: flex;
  align-items: center;
  cursor: pointer;
  flex-shrink: 0;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  width: 48px;
  height: 26px;
  background: var(--bg-hover);
  border-radius: 13px;
  position: relative;
  transition: background var(--transition-fast);
}

.toggle-slider::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
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
  transform: translateX(22px);
}

/* 滑块输入 */
.slider-input {
  display: flex;
  align-items: center;
  gap: 16px;
}

.slider-input input[type="range"] {
  flex: 1;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--bg-hover);
  border-radius: 3px;
  outline: none;
}

.slider-input input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  background: var(--primary);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(59, 130, 246, 0.4);
}

.slider-input input[type="range"]::-moz-range-thumb {
  width: 18px;
  height: 18px;
  background: var(--primary);
  border-radius: 50%;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 6px rgba(59, 130, 246, 0.4);
}

.slider-value {
  min-width: 48px;
  text-align: right;
  font-size: 14px;
  font-weight: 500;
  color: var(--primary);
}
</style>
