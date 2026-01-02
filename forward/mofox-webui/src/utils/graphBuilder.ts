/**
 * 关系图谱数据构建工具
 * 用于将用户数据转换为ECharts图谱格式
 */

import type { PersonCard } from '@/api/relationship'

export interface GraphNode {
  id: string
  name: string
  platform: string
  relationship_score: number
  know_times: number
  category: string
  symbolSize: number
  itemStyle: {
    color: string
    borderColor?: string
    borderWidth?: number
  }
  label?: {
    show: boolean
  }
}

export interface GraphEdge {
  source: string
  target: string
  value: number
  lineStyle: {
    width: number
    color: string
    type?: 'solid' | 'dashed'
  }
}

export interface GraphCategory {
  name: string
  itemStyle: {
    color: string
  }
}

/**
 * 从person_id中提取平台名称
 */
export function extractPlatform(personId: string): string {
  const parts = personId.split(':')
  return parts.length > 1 && parts[0] ? parts[0] : 'unknown'
}

/**
 * 根据平台获取颜色
 */
export function getPlatformColor(platform: string): string {
  const colors: Record<string, string> = {
    'qq': '#12B7F5',
    'wechat': '#07C160',
    'web_ui_chatroom': '#6366F1',
    'telegram': '#0088CC',
    'discord': '#5865F2',
    'default': '#94A3B8'
  }
  return colors[platform] || colors['default']
}

/**
 * 根据认识次数计算节点大小
 */
export function calculateNodeSize(knowTimes: number): number {
  const baseSize = 30
  const maxSize = 80
  const size = baseSize + (knowTimes / 10)
  return Math.min(size, maxSize)
}

/**
 * 根据关系强度获取边的颜色
 */
export function getEdgeColor(strength: number): string {
  if (strength > 0.7) return '#10B981'  // 强关系 - 绿色
  if (strength > 0.4) return '#F59E0B'  // 中等关系 - 橙色
  return '#94A3B8'  // 弱关系 - 灰色
}

/**
 * 计算两个节点之间的关系强度
 */
export function calculateRelationshipStrength(
  node1: GraphNode,
  node2: GraphNode
): number {
  // 基于关系分数的平均值
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

/**
 * 构建图谱节点
 */
export function buildGraphNodes(persons: PersonCard[]): GraphNode[] {
  return persons.map(person => {
    const platform = extractPlatform(person.person_id)
    return {
      id: person.person_id,
      name: person.nickname || person.person_name,
      platform,
      relationship_score: person.relationship_score,
      know_times: person.know_times,
      category: platform,
      symbolSize: calculateNodeSize(person.know_times),
      itemStyle: {
        color: getPlatformColor(platform)
      },
      label: {
        show: true
      }
    }
  })
}

/**
 * 构建图谱边（优化版本，限制每个节点的最大边数）
 */
export function buildGraphEdges(
  nodes: GraphNode[],
  maxEdgesPerNode: number = 5,
  minStrength: number = 0.3
): GraphEdge[] {
  const edges: GraphEdge[] = []
  const addedEdges = new Set<string>()
  
  for (const node of nodes) {
    const nodeEdges: Array<{ target: GraphNode; strength: number }> = []
    
    // 计算当前节点与其他所有节点的关系强度
    for (const otherNode of nodes) {
      if (node.id === otherNode.id) continue
      
      const strength = calculateRelationshipStrength(node, otherNode)
      if (strength >= minStrength) {
        nodeEdges.push({ target: otherNode, strength })
      }
    }
    
    // 按强度排序，只保留最强的N条边
    nodeEdges.sort((a, b) => b.strength - a.strength)
    nodeEdges.slice(0, maxEdgesPerNode).forEach(({ target, strength }) => {
      // 避免重复添加边（A-B 和 B-A 是同一条边）
      const edgeKey = [node.id, target.id].sort().join('-')
      if (!addedEdges.has(edgeKey)) {
        addedEdges.add(edgeKey)
        edges.push({
          source: node.id,
          target: target.id,
          value: strength,
          lineStyle: {
            width: strength * 5,
            color: getEdgeColor(strength),
            type: strength > 0.6 ? 'solid' : 'dashed'
          }
        })
      }
    })
  }
  
  return edges
}

/**
 * 构建图谱分类
 */
export function buildGraphCategories(nodes: GraphNode[]): GraphCategory[] {
  const platformSet = new Set(nodes.map(n => n.platform))
  return Array.from(platformSet).map(platform => ({
    name: platform,
    itemStyle: {
      color: getPlatformColor(platform)
    }
  }))
}

/**
 * 高亮指定节点（用于个人中心视图）
 */
export function highlightCenterNode(nodes: GraphNode[], centerId: string): GraphNode[] {
  return nodes.map(node => {
    if (node.id === centerId) {
      return {
        ...node,
        symbolSize: node.symbolSize * 1.5,
        itemStyle: {
          ...node.itemStyle,
          borderColor: '#EF4444',
          borderWidth: 3
        }
      }
    }
    return node
  })
}

/**
 * 计算图谱统计信息
 */
export function calculateGraphStats(nodes: GraphNode[], edges: GraphEdge[]) {
  const totalNodes = nodes.length
  const totalEdges = edges.length
  const avgScore = totalNodes > 0
    ? nodes.reduce((sum, n) => sum + n.relationship_score, 0) / totalNodes
    : 0
  
  const maxScore = totalNodes > 0
    ? Math.max(...nodes.map(n => n.relationship_score))
    : 0
  
  const minScore = totalNodes > 0
    ? Math.min(...nodes.map(n => n.relationship_score))
    : 0
  
  // 统计孤立节点（没有边连接的节点）
  const connectedNodes = new Set<string>()
  edges.forEach(edge => {
    connectedNodes.add(edge.source)
    connectedNodes.add(edge.target)
  })
  const isolatedNodes = nodes.filter(n => !connectedNodes.has(n.id)).length
  
  return {
    total_nodes: totalNodes,
    total_edges: totalEdges,
    avg_score: avgScore,
    max_score: maxScore,
    min_score: minScore,
    isolated_nodes: isolatedNodes
  }
}