# 关系图谱可视化功能设计文档

## 功能概述

在关系管理页面添加关系图谱可视化功能，以图形化方式展示用户之间的关系网络，帮助用户直观地理解和管理人际关系。

## 功能目标

1. **可视化展示**：以节点和连线的方式展示用户关系网络
2. **交互操作**：支持节点拖拽、缩放、点击查看详情等交互
3. **关系分析**：通过颜色、大小等视觉元素表示关系强度
4. **数据洞察**：提供关系统计和分析功能

## 技术选型

### 前端图形库选择

推荐使用以下库之一：

1. **D3.js** (推荐)
   - 优点：功能强大、灵活性高、社区活跃
   - 缺点：学习曲线较陡
   - 适用场景：需要高度自定义的复杂图谱

2. **ECharts**
   - 优点：中文文档完善、配置简单、性能好
   - 缺点：自定义能力相对较弱
   - 适用场景：快速实现标准图谱

3. **Cytoscape.js**
   - 优点：专为网络图设计、性能优秀
   - 缺点：样式定制相对复杂
   - 适用场景：大规模网络图

**最终选择：ECharts**
- 理由：与项目现有技术栈契合，学习成本低，文档完善，能满足基本需求

## 功能设计

### 1. 图谱视图模式

#### 1.1 全局视图
- 展示所有用户及其关系
- 支持按平台筛选
- 支持按关系强度筛选

#### 1.2 个人中心视图
- 以某个用户为中心展示其关系网络
- 显示直接关系和间接关系（可配置层级）

#### 1.3 群组视图
- 按平台或自定义标签分组展示
- 显示组内和组间关系

### 2. 节点设计

#### 2.1 节点属性
```typescript
interface GraphNode {
  id: string              // person_id
  name: string           // 用户名
  nickname?: string      // 昵称
  platform: string       // 平台
  avatar?: string        // 头像
  relationshipScore: number  // 关系分数
  knowTimes: number      // 认识次数
  category: string       // 分类（用于颜色区分）
}
```

#### 2.2 节点视觉设计
- **大小**：根据 `knowTimes`（认识次数）决定
- **颜色**：根据 `platform`（平台）区分
- **边框**：根据 `relationshipScore`（关系分数）设置粗细
- **图标**：显示平台图标或用户头像

### 3. 连线设计

#### 3.1 连线属性
```typescript
interface GraphEdge {
  source: string         // 源节点ID
  target: string         // 目标节点ID
  value: number         // 关系强度（0-1）
  type: string          // 关系类型
}
```

#### 3.2 连线视觉设计
- **粗细**：根据关系强度决定
- **颜色**：根据关系类型区分
  - 强关系（>0.7）：深色
  - 中等关系（0.4-0.7）：中等色
  - 弱关系（<0.4）：浅色
- **样式**：实线表示直接关系，虚线表示间接关系

### 4. 交互功能

#### 4.1 基础交互
- **拖拽**：拖动节点调整位置
- **缩放**：鼠标滚轮缩放图谱
- **平移**：拖动画布平移视图
- **点击节点**：显示用户详情卡片
- **悬停节点**：高亮显示相关连线

#### 4.2 高级交互
- **搜索定位**：搜索用户并定位到节点
- **筛选**：按平台、关系强度筛选
- **布局切换**：力导向布局、环形布局、树形布局
- **导出**：导出为图片或数据

### 5. 数据分析

#### 5.1 统计指标
- 总用户数
- 平均关系强度
- 最强关系Top 10
- 孤立节点数量
- 关系密度

#### 5.2 关系发现
- 共同好友推荐
- 关系链路分析
- 社群检测

## API设计

### 1. 获取图谱数据

```typescript
GET /api/relationship/graph

Query Parameters:
- platform?: string        // 平台筛选
- min_score?: number      // 最小关系分数
- max_nodes?: number      // 最大节点数
- center_person?: string  // 中心用户ID（个人中心视图）
- depth?: number          // 关系深度（默认1）

Response:
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "qq:123456",
        "name": "张三",
        "nickname": "小张",
        "platform": "qq",
        "relationship_score": 0.85,
        "know_times": 150,
        "category": "qq"
      }
    ],
    "edges": [
      {
        "source": "qq:123456",
        "target": "qq:789012",
        "value": 0.75,
        "type": "direct"
      }
    ],
    "stats": {
      "total_nodes": 50,
      "total_edges": 120,
      "avg_score": 0.65
    }
  }
}
```

### 2. 获取节点详情

```typescript
GET /api/relationship/graph/node/{person_id}

Response:
{
  "success": true,
  "data": {
    "basic_info": { ... },
    "relationship": { ... },
    "connections": [
      {
        "person_id": "qq:789012",
        "person_name": "李四",
        "relationship_score": 0.75
      }
    ]
  }
}
```

## 实现计划

### Phase 1: 基础功能（1-2周）
- [ ] 后端API开发
  - [ ] 图谱数据查询接口
  - [ ] 关系计算逻辑
  - [ ] 数据聚合和优化
- [ ] 前端基础组件
  - [ ] 图谱容器组件
  - [ ] ECharts集成
  - [ ] 基础布局实现

### Phase 2: 交互优化（1周）
- [ ] 节点交互
  - [ ] 点击查看详情
  - [ ] 悬停高亮
  - [ ] 拖拽调整
- [ ] 视图控制
  - [ ] 缩放和平移
  - [ ] 搜索定位
  - [ ] 筛选功能

### Phase 3: 高级功能（1-2周）
- [ ] 多种布局算法
- [ ] 数据分析面板
- [ ] 导出功能
- [ ] 性能优化（大数据量处理）

### Phase 4: 优化和测试（1周）
- [ ] 性能测试和优化
- [ ] 用户体验优化
- [ ] 文档完善
- [ ] Bug修复

## 技术实现要点

### 1. 关系计算

```python
# 后端关系强度计算
def calculate_relationship_strength(person1_id: str, person2_id: str) -> float:
    """
    计算两个用户之间的关系强度
    
    考虑因素：
    1. 直接关系分数
    2. 共同交互次数
    3. 时间衰减
    """
    # 获取两个用户的关系数据
    rel1 = get_relationship(person1_id)
    rel2 = get_relationship(person2_id)
    
    # 计算关系强度
    strength = (rel1.relationship_score + rel2.relationship_score) / 2
    
    # 考虑交互频率
    interaction_factor = min(rel1.know_times, rel2.know_times) / 100
    strength = strength * (1 + interaction_factor * 0.2)
    
    # 时间衰减
    time_factor = calculate_time_decay(rel1.last_know, rel2.last_know)
    strength = strength * time_factor
    
    return min(strength, 1.0)
```

### 2. 图谱布局

```typescript
// 前端ECharts配置
const graphOption = {
  series: [{
    type: 'graph',
    layout: 'force',
    data: nodes,
    links: edges,
    roam: true,
    label: {
      show: true,
      position: 'right'
    },
    force: {
      repulsion: 100,
      edgeLength: [50, 200],
      gravity: 0.1
    },
    emphasis: {
      focus: 'adjacency',
      lineStyle: {
        width: 3
      }
    }
  }]
}
```

### 3. 性能优化策略

```typescript
// 1. 边计算优化 - 限制每个节点的最大边数
function buildOptimizedEdges(nodes: GraphNode[], maxEdgesPerNode = 5) {
  const edges: GraphEdge[] = []
  
  for (const node of nodes) {
    const nodeEdges: Array<{target: GraphNode, strength: number}> = []
    
    for (const otherNode of nodes) {
      if (node.id === otherNode.id) continue
      const strength = calculateRelationshipStrength(node, otherNode)
      if (strength > 0.3) {
        nodeEdges.push({ target: otherNode, strength })
      }
    }
    
    // 只保留最强的N条边
    nodeEdges.sort((a, b) => b.strength - a.strength)
    nodeEdges.slice(0, maxEdgesPerNode).forEach(({ target, strength }) => {
      edges.push({
        source: node.id,
        target: target.id,
        value: strength
      })
    })
  }
  
  return edges
}

// 2. 数据缓存
const graphCache = new Map()
const CACHE_DURATION = 5 * 60 * 1000 // 5分钟

async function loadGraphDataWithCache(options) {
  const cacheKey = JSON.stringify(options)
  const cached = graphCache.get(cacheKey)
  
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data
  }
  
  const data = await loadGraphData(options)
  graphCache.set(cacheKey, { data, timestamp: Date.now() })
  return data
}

// 3. 分页加载大数据
async function loadLargeGraph() {
  let allPersons = []
  let page = 1
  
  while (true) {
    const response = await getPersonList(page, 50)
    if (!response.success) break
    
    allPersons = [...allPersons, ...response.data.persons]
    if (page >= response.data.total_pages) break
    page++
  }
  
  return buildGraph(allPersons)
}
```

## UI设计

### 1. 布局结构

```
┌─────────────────────────────────────────────┐
│  关系图谱                    [筛选] [布局] [导出] │
├─────────────────────────────────────────────┤
│                                             │
│                                             │
│              图谱可视化区域                    │
│                                             │
│                                             │
├─────────────────────────────────────────────┤
│  统计面板                                     │
│  总用户: 50  平均关系: 0.65  最强关系: 0.95    │
└─────────────────────────────────────────────┘
```

### 2. 配色方案

- **QQ平台**：#12B7F5（蓝色）
- **微信平台**：#07C160（绿色）
- **Web UI**：#6366F1（紫色）
- **其他平台**：#94A3B8（灰色）

### 3. 响应式设计

- 桌面端：全屏显示，侧边栏展示详情
- 平板端：适配触摸操作
- 移动端：简化视图，重点展示核心关系

## 测试计划

### 1. 功能测试
- [ ] 图谱正确渲染
- [ ] 交互功能正常
- [ ] 数据筛选准确
- [ ] 详情展示完整

### 2. 性能测试
- [ ] 100个节点加载时间 < 1s
- [ ] 500个节点加载时间 < 3s
- [ ] 1000个节点加载时间 < 5s
- [ ] 交互响应时间 < 100ms

### 3. 兼容性测试
- [ ] Chrome 90+
- [ ] Firefox 88+
- [ ] Safari 14+
- [ ] Edge 90+

## 未来扩展

1. **AI分析**：使用AI分析关系模式，提供智能建议
2. **时间轴**：展示关系随时间的变化
3. **3D图谱**：使用Three.js实现3D关系网络
4. **协作功能**：多人同时查看和编辑关系图谱
5. **移动端App**：开发独立的移动端应用

## 参考资料

- [ECharts 关系图文档](https://echarts.apache.org/zh/option.html#series-graph)
- [D3.js Force Layout](https://d3js.org/d3-force)
- [Cytoscape.js 文档](https://js.cytoscape.org/)
- [社交网络分析理论](https://en.wikipedia.org/wiki/Social_network_analysis)

## 更新日志

- 2026-01-02: 初始版本，完成功能设计和技术选型