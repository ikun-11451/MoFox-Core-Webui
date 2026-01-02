<template>
  <div class="relationship-graph">
    <!-- 控制面板 -->
    <div class="graph-controls">
      <div class="control-group">
        <label class="control-label">
          <span class="material-symbols-rounded">filter_list</span>
          <span>平台筛选</span>
        </label>
        <select v-model="selectedPlatform" class="m3-select" @change="handleFilterChange">
          <option value="">全部平台</option>
          <option v-for="platform in platforms" :key="platform.platform" :value="platform.platform">
            {{ platform.platform }} ({{ platform.count }})
          </option>
        </select>
      </div>

      <div class="control-group">
        <label class="control-label">
          <span class="material-symbols-rounded">tune</span>
          <span>最小关系分数</span>
        </label>
        <input 
          v-model.number="minScore" 
          type="range" 
          min="0" 
          max="100" 
          class="m3-slider"
          @change="handleFilterChange"
        />
        <span class="score-value">{{ minScore }}%</span>
      </div>

      <div class="control-group">
        <label class="control-label">
          <span class="material-symbols-rounded">account_tree</span>
          <span>布局</span>
        </label>
        <select v-model="layoutType" class="m3-select" @change="handleLayoutChange">
          <option value="force">力导向布局</option>
          <option value="circular">环形布局</option>
        </select>
      </div>

      <button class="m3-button text" @click="resetView">
        <span class="material-symbols-rounded">refresh</span>
        <span>重置视图</span>
      </button>
    </div>

    <!-- 图谱画布 -->
    <div class="graph-canvas" ref="chartContainer"></div>

    <!-- 统计面板 -->
    <div class="graph-stats">
      <div class="stat-item">
        <span class="stat-label">节点数</span>
        <span class="stat-value">{{ stats.total_nodes }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">关系数</span>
        <span class="stat-value">{{ stats.total_edges }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">平均分数</span>
        <span class="stat-value">{{ (stats.avg_score * 100).toFixed(0) }}%</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">孤立节点</span>
        <span class="stat-value">{{ stats.isolated_nodes }}</span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <span class="material-symbols-rounded spinning">progress_activity</span>
      <p>加载图谱数据...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import { getPersonList, getPlatforms, getPersonDetail } from '@/api/relationship'
import type { PlatformInfo } from '@/api/relationship'
import {
  buildGraphNodes,
  buildGraphEdges,
  buildGraphCategories,
  calculateGraphStats,
  type GraphNode,
  type GraphEdge
} from '@/utils/graphBuilder'

const props = defineProps<{
  centerPersonId?: string  // 如果提供，则显示个人中心视图
}>()

const emit = defineEmits<{
  nodeClick: [personId: string]
}>()

// 状态
const chartContainer = ref<HTMLElement>()
const chart = ref<ECharts>()
const loading = ref(false)
const nodes = ref<GraphNode[]>([])
const edges = ref<GraphEdge[]>([])
const platforms = ref<PlatformInfo[]>([])

// 筛选条件
const selectedPlatform = ref('')
const minScore = ref(0)
const layoutType = ref<'force' | 'circular'>('force')

// 统计信息
const stats = ref({
  total_nodes: 0,
  total_edges: 0,
  avg_score: 0,
  max_score: 0,
  min_score: 0,
  isolated_nodes: 0
})

// 加载图谱数据
async function loadGraphData() {
  loading.value = true
  
  try {
    // 1. 加载平台列表
    const platformsResult = await getPlatforms()
    if (platformsResult.success && platformsResult.data) {
      platforms.value = platformsResult.data.platforms
    }

    // 2. 加载用户列表
    const result = await getPersonList(
      1,
      200,  // 最多加载200个用户
      selectedPlatform.value || undefined
    )

    if (result.success && result.data) {
      // 3. 过滤低分用户
      const filteredPersons = result.data.persons.filter(
        p => p.relationship_score >= minScore.value / 100
      )

      // 4. 构建节点
      nodes.value = buildGraphNodes(filteredPersons)

      // 5. 构建边
      edges.value = buildGraphEdges(nodes.value, 5, 0.3)

      // 6. 计算统计
      stats.value = calculateGraphStats(nodes.value, edges.value)

      // 7. 渲染图谱
      renderGraph()
    }
  } catch (error) {
    console.error('加载图谱数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 渲染图谱
function renderGraph() {
  if (!chartContainer.value) return

  // 初始化或获取图表实例
  if (!chart.value) {
    chart.value = echarts.init(chartContainer.value)
  }

  const categories = buildGraphCategories(nodes.value)

  const option: echarts.EChartsOption = {
    title: {
      text: '关系图谱',
      left: 'center',
      top: 10,
      textStyle: {
        color: 'var(--md-sys-color-on-surface)',
        fontSize: 18,
        fontWeight: 500
      }
    },
    tooltip: {
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          const node = params.data as GraphNode
          return `
            <div style="padding: 8px;">
              <strong style="font-size: 14px;">${node.name}</strong><br/>
              <span style="color: #666;">平台: ${node.platform}</span><br/>
              <span style="color: #666;">关系分数: ${(node.relationship_score * 100).toFixed(0)}%</span><br/>
              <span style="color: #666;">交互次数: ${node.know_times}</span>
            </div>
          `
        } else if (params.dataType === 'edge') {
          const edge = params.data as GraphEdge
          return `关系强度: ${(edge.value * 100).toFixed(0)}%`
        }
        return ''
      },
      backgroundColor: 'var(--md-sys-color-surface-container-high)',
      borderColor: 'var(--md-sys-color-outline)',
      textStyle: {
        color: 'var(--md-sys-color-on-surface)'
      }
    },
    legend: {
      data: categories.map(c => c.name),
      orient: 'vertical',
      left: 10,
      top: 50,
      textStyle: {
        color: 'var(--md-sys-color-on-surface)'
      }
    },
    series: [{
      type: 'graph',
      layout: layoutType.value,
      data: nodes.value,
      links: edges.value,
      categories: categories,
      roam: true,
      label: {
        show: true,
        position: 'right',
        formatter: '{b}',
        fontSize: 12,
        color: 'var(--md-sys-color-on-surface)'
      },
      labelLayout: {
        hideOverlap: true
      },
      scaleLimit: {
        min: 0.4,
        max: 2
      },
      lineStyle: {
        color: 'source',
        curveness: 0.3
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 10
        },
        label: {
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      force: layoutType.value === 'force' ? {
        repulsion: 100,
        edgeLength: [50, 200],
        gravity: 0.1,
        friction: 0.6
      } : undefined,
      circular: layoutType.value === 'circular' ? {
        rotateLabel: true
      } : undefined
    }]
  }

  chart.value.setOption(option)

  // 添加点击事件
  chart.value.off('click')
  chart.value.on('click', (params: any) => {
    if (params.dataType === 'node') {
      emit('nodeClick', params.data.id)
    }
  })
}

// 处理筛选变化
function handleFilterChange() {
  loadGraphData()
}

// 处理布局变化
function handleLayoutChange() {
  renderGraph()
}

// 重置视图
function resetView() {
  if (chart.value) {
    chart.value.dispatchAction({
      type: 'restore'
    })
  }
}

// 响应式调整
function handleResize() {
  chart.value?.resize()
}

// 生命周期
onMounted(() => {
  loadGraphData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart.value?.dispose()
})

// 监听中心节点变化
watch(() => props.centerPersonId, () => {
  if (props.centerPersonId) {
    // TODO: 实现个人中心视图
    loadGraphData()
  }
})
</script>

<style scoped>
.relationship-graph {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--md-sys-color-surface);
  border-radius: 16px;
  overflow: hidden;
}

.graph-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background: var(--md-sys-color-surface-container-low);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
  white-space: nowrap;
}

.control-label .material-symbols-rounded {
  font-size: 18px;
}

.m3-select {
  padding: 8px 12px;
  border: 1px solid var(--md-sys-color-outline);
  border-radius: 8px;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  font-size: 14px;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
}

.m3-select:hover {
  border-color: var(--md-sys-color-primary);
}

.m3-select:focus {
  border-color: var(--md-sys-color-primary);
  box-shadow: 0 0 0 3px var(--md-sys-color-primary-container);
}

.m3-slider {
  width: 120px;
  height: 4px;
  border-radius: 2px;
  background: var(--md-sys-color-surface-container-highest);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
}

.m3-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--md-sys-color-primary);
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.m3-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--md-sys-color-primary);
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.score-value {
  min-width: 40px;
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--md-sys-color-primary);
}

.graph-canvas {
  flex: 1;
  min-height: 500px;
}

.graph-stats {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 16px 24px;
  background: var(--md-sys-color-surface-container-low);
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--md-sys-color-on-surface-variant);
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--md-sys-color-primary);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: white;
  z-index: 10;
}

.loading-overlay .material-symbols-rounded {
  font-size: 48px;
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
  .graph-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .control-group {
    flex-direction: column;
    align-items: stretch;
  }

  .m3-slider {
    width: 100%;
  }

  .graph-stats {
    flex-wrap: wrap;
    gap: 16px;
  }
}
</style>