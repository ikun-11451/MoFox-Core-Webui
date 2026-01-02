# 关系图谱 API 设计文档

## 设计原则

**利用现有API，不新增API端点**

关系图谱功能将完全基于现有的 `/api/relationship` 接口实现，通过前端数据处理和计算来构建图谱。

## 使用的现有API

### 1. 获取用户列表 - `/api/relationship/list`

**用途**：获取所有用户作为图谱节点

#### 现有接口
```
GET /api/relationship/list?page=1&page_size=100&platform=qq
```

#### 返回数据
```json
{
  "persons": [
    {
      "person_id": "qq:123456",
      "person_name": "张三",
      "nickname": "小张",
      "relationship_score": 0.85,
      "relationship_text": "好朋友",
      "short_impression": "热心肠",
      "know_times": 150,
      "last_know": "1704096000"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 100,
  "total_pages": 1
}
```

#### 图谱用途
- 作为图谱的**节点数据源**
- 提供节点的基础属性（名称、平台、关系分数等）

---

### 2. 获取用户详情 - `/api/relationship/person/{person_id}`

**用途**：获取节点的详细信息

#### 现有接口
```
GET /api/relationship/person/qq:123456
```

#### 返回数据
```json
{
  "basic_info": {
    "person_id": "qq:123456",
    "person_name": "张三",
    "nickname": "小张",
    "know_times": 150,
    "know_since": "1688140800",
    "last_know": "1704096000",
    "attitude": 85
  },
  "relationship": {
    "person_id": "qq:123456",
    "person_name": "张三",
    "relationship_score": 0.85,
    "relationship_text": "好朋友"
  },
  "impression": "热心肠，乐于助人",
  "short_impression": "热心肠",
  "memory_points": [
    {
      "content": "帮我解决了技术问题",
      "weight": 0.9,
      "timestamp": "1704096000"
    }
  ]
}
```

#### 图谱用途
- 点击节点时显示**详细信息**
- 提供更丰富的用户背景数据

---

### 3. 获取平台列表 - `/api/relationship/platforms`

**用途**：获取所有平台用于筛选

#### 现有接口
```
GET /api/relationship/platforms
```

#### 返回数据
```json
{
  "platforms": [
    {
      "platform": "qq",
      "count": 80
    },
    {
      "platform": "wechat",
      "count": 50
    },
    {
      "platform": "web_ui_chatroom",
      "count": 20
    }
  ]
}
```

#### 图谱用途
- 提供**平台筛选选项**
- 用于节点分类和着色

---

### 4. 获取关系统计 - `/api/relationship/stats`

**用途**：获取整体统计数据

#### 现有接口
```
GET /api/relationship/stats
```

#### 返回数据
```json
{
  "total_users": 150,
  "users_with_impression": 89
}
```

#### 图谱用途
- 显示在图谱的**统计面板**
- 提供数据概览

---

## 前端数据处理策略

### 1. 构建图谱节点

```typescript
// src/utils/graphBuilder.ts

interface PersonCard {
  person_id: string
  person_name: string
  nickname?: string
  relationship_score: number
  know_times: number
}

function buildGraphNodes(persons: PersonCard[]): GraphNode[] {
  return persons.map(person => ({
    id: person.person_id,
    name: person.nickname || person.person_name,
    platform: extractPlatform(person.person_id),
    relationship_score: person.relationship_score,
    know_times: person.know_times,
    category: extractPlatform(person.person_id),
    symbolSize: calculateNodeSize(person.know_times),
    itemStyle: {
      color: getPlatformColor(extractPlatform(person.person_id))
    }
  }))
}

function extractPlatform(personId: string): string {
  // person_id 格式: "platform:user_id"
  return personId.split(':')[0] || 'unknown'
}

function calculateNodeSize(knowTimes: number): number {
  const baseSize = 30
  const maxSize = 80
  const size = baseSize + (knowTimes / 10)
  return Math.min(size, maxSize)
}

function getPlatformColor(platform: string): string {
  const colors: Record<string, string> = {
    'qq': '#12B7F5',
    'wechat': '#07C160',
    'web_ui_chatroom': '#6366F1',
    'default': '#94A3B8'
  }
  return colors[platform] || colors.default
}
```

### 2. 计算关系边

```typescript
function buildGraphEdges(nodes: GraphNode[]): GraphEdge[] {
  const edges: GraphEdge[] = []
  
  // 基于关系分数计算边
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const node1 = nodes[i]
      const node2 = nodes[j]
      
      // 计算关系强度
      const strength = calculateRelationshipStrength(node1, node2)
      
      // 只显示有意义的关系（强度 > 0.3）
      if (strength > 0.3) {
        edges.append({
          source: node1.id,
          target: node2.id,
          value: strength,
          lineStyle: {
            width: strength * 5,
            color: getEdgeColor(strength),
            type: strength > 0.6 ? 'solid' : 'dashed'
          }
        })
      }
    }
  }
  
  return edges
}

function calculateRelationshipStrength(
  node1: GraphNode, 
  node2: GraphNode
): number {
  // 简化算法：基于关系分数的平均值
  const avgScore = (node1.relationship_score + node2.relationship_score) / 2
  
  // 同平台的用户关系更强
  const platformBonus = node1.platform === node2.platform ? 0.1 : 0
  
  // 交互次数影响
  const interactionFactor = Math.min(
    (node1.know_times + node2.know_times) / 500,
    0.2
  )
  
  return Math.min(avgScore + platformBonus + interactionFactor, 1.0)
}

function getEdgeColor(strength: number): string {
  if (strength > 0.7) return '#10B981'  // 强关系 - 绿色
  if (strength > 0.4) return '#F59E0B'  // 中等关系 - 橙色
  return '#94A3B8'  // 弱关系 - 灰色
}
```

### 3. 数据加载流程

```typescript
// src/composables/useRelationshipGraph.ts

export function useRelationshipGraph() {
  const nodes = ref<GraphNode[]>([])
  const edges = ref<GraphEdge[]>([])
  const loading = ref(false)
  const stats = ref({
    total_nodes: 0,
    total_edges: 0,
    avg_score: 0
  })
  
  async function loadGraphData(options: {
    platform?: string
    minScore?: number
    maxNodes?: number
  }) {
    loading.value = true
    
    try {
      // 1. 获取用户列表
      const response = await getPersonList(
        1,
        options.maxNodes || 100,
        options.platform
      )
      
      if (response.success && response.data) {
        // 2. 过滤低分用户
        const filteredPersons = response.data.persons.filter(
          p => p.relationship_score >= (options.minScore || 0)
        )
        
        // 3. 构建节点
        nodes.value = buildGraphNodes(filteredPersons)
        
        // 4. 计算边
        edges.value = buildGraphEdges(nodes.value)
        
        // 5. 计算统计
        stats.value = {
          total_nodes: nodes.value.length,
          total_edges: edges.value.length,
          avg_score: nodes.value.reduce((sum, n) => sum + n.relationship_score, 0) / nodes.value.length
        }
      }
    } catch (error) {
      console.error('加载图谱数据失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  return {
    nodes,
    edges,
    stats,
    loading,
    loadGraphData
  }
}
```

### 4. 个人中心视图

```typescript
async function loadPersonCenteredGraph(personId: string, depth: number = 1) {
  // 1. 获取中心用户详情
  const centerPerson = await getPersonDetail(personId)
  
  // 2. 获取所有用户
  const allPersons = await getPersonList(1, 200)
  
  // 3. 筛选相关用户（基于关系分数）
  const relatedPersons = allPersons.data.persons.filter(p => {
    if (p.person_id === personId) return true
    
    // 计算与中心用户的关系强度
    const strength = calculateRelationshipStrength(
      centerPerson.data,
      p
    )
    
    return strength > 0.4  // 只显示中等以上关系
  })
  
  // 4. 构建图谱
  nodes.value = buildGraphNodes(relatedPersons)
  edges.value = buildGraphEdges(nodes.value)
  
  // 5. 高亮中心节点
  const centerNode = nodes.value.find(n => n.id === personId)
  if (centerNode) {
    centerNode.symbolSize = (centerNode.symbolSize || 50) * 1.5
    centerNode.itemStyle = {
      ...centerNode.itemStyle,
      borderColor: '#EF4444',
      borderWidth: 3
    }
  }
}
```

## 前端组件结构

```
RelationshipGraphView.vue
├── GraphControls.vue (筛选、布局控制)
├── GraphCanvas.vue (ECharts 图谱)
├── GraphStats.vue (统计面板)
└── NodeDetailDialog.vue (节点详情弹窗)
```

## ECharts 配置示例

```typescript
const graphOption = computed(() => ({
  title: {
    text: '关系图谱',
    left: 'center'
  },
  tooltip: {
    formatter: (params: any) => {
      if (params.dataType === 'node') {
        return `
          <strong>${params.data.name}</strong><br/>
          平台: ${params.data.platform}<br/>
          关系分数: ${(params.data.relationship_score * 100).toFixed(0)}%<br/>
          交互次数: ${params.data.know_times}
        `
      } else {
        return `关系强度: ${(params.data.value * 100).toFixed(0)}%`
      }
    }
  },
  series: [{
    type: 'graph',
    layout: 'force',
    data: nodes.value,
    links: edges.value,
    categories: categories.value,
    roam: true,
    label: {
      show: true,
      position: 'right',
      formatter: '{b}'
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
      }
    },
    force: {
      repulsion: 100,
      edgeLength: [50, 200],
      gravity: 0.1
    }
  }]
}))
```

## 性能优化策略

### 1. 数据分页加载
```typescript
// 大数据量时分批加载
async function loadLargeGraph() {
  const pageSize = 50
  let page = 1
  let allPersons: PersonCard[] = []
  
  while (true) {
    const response = await getPersonList(page, pageSize)
    if (!response.success || !response.data) break
    
    allPersons = [...allPersons, ...response.data.persons]
    
    if (page >= response.data.total_pages) break
    page++
  }
  
  // 构建图谱
  nodes.value = buildGraphNodes(allPersons)
  edges.value = buildGraphEdges(nodes.value)
}
```

### 2. 边计算优化
```typescript
// 只计算必要的边，避免O(n²)复杂度
function buildOptimizedEdges(nodes: GraphNode[], maxEdgesPerNode: number = 5): GraphEdge[] {
  const edges: GraphEdge[] = []
  
  for (const node of nodes) {
    // 为每个节点只保留最强的N条边
    const nodeEdges: Array<{target: GraphNode, strength: number}> = []
    
    for (const otherNode of nodes) {
      if (node.id === otherNode.id) continue
      
      const strength = calculateRelationshipStrength(node, otherNode)
      if (strength > 0.3) {
        nodeEdges.push({ target: otherNode, strength })
      }
    }
    
    // 排序并取前N个
    nodeEdges.sort((a, b) => b.strength - a.strength)
    nodeEdges.slice(0, maxEdgesPerNode).forEach(({ target, strength }) => {
      edges.push({
        source: node.id,
        target: target.id,
        value: strength,
        lineStyle: {
          width: strength * 5,
          color: getEdgeColor(strength)
        }
      })
    })
  }
  
  return edges
}
```

### 3. 缓存策略
```typescript
// 缓存图谱数据
const graphCache = new Map<string, { nodes: GraphNode[], edges: GraphEdge[], timestamp: number }>()
const CACHE_DURATION = 5 * 60 * 1000 // 5分钟

async function loadGraphDataWithCache(options: GraphOptions) {
  const cacheKey = JSON.stringify(options)
  const cached = graphCache.get(cacheKey)
  
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    nodes.value = cached.nodes
    edges.value = cached.edges
    return
  }
  
  // 加载新数据
  await loadGraphData(options)
  
  // 更新缓存
  graphCache.set(cacheKey, {
    nodes: nodes.value,
    edges: edges.value,
    timestamp: Date.now()
  })
}
```

## 实现优先级

### Phase 1: 基础图谱（MVP）
- [x] 使用现有API获取用户列表
- [ ] 前端构建节点数据
- [ ] 简单的边计算（基于关系分数）
- [ ] ECharts基础图谱渲染
- [ ] 平台筛选功能

### Phase 2: 交互优化
- [ ] 节点点击查看详情
- [ ] 节点悬停高亮
- [ ] 缩放和平移
- [ ] 搜索定位功能

### Phase 3: 高级功能
- [ ] 个人中心视图
- [ ] 多种布局算法
- [ ] 统计分析面板
- [ ] 导出功能

## 总结

通过利用现有的4个API接口，我们可以完全在前端实现关系图谱功能：

1. **`/api/relationship/list`** - 提供节点数据
2. **`/api/relationship/person/{id}`** - 提供节点详情
3. **`/api/relationship/platforms`** - 提供筛选选项
4. **`/api/relationship/stats`** - 提供统计数据

关键是在前端实现：
- 节点构建逻辑
- 边计算算法
- 数据缓存和优化
- 图谱渲染和交互

这种方案的优点：
- ✅ 不需要修改后端
- ✅ 灵活的前端控制
- ✅ 易于迭代和优化
- ✅ 降低服务器负担

## 更新日志

- 2026-01-02: 重新设计，基于现有API实现