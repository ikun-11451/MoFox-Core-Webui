/**
 * Mock 数据用于 Demo 模式
 */

export const MOCK_DATA = {
  // 登录
  login: {
    success: true,
    data: {
      success: true,
      token: 'demo-token'
    }
  },

  // 仪表盘概览
  overview: {
    success: true,
    data: {
      system: {
        cpu_percent: 15.5,
        memory_usage_mb: 450,
        uptime_seconds: 123456
      },
      chats: {
        total_streams: 128,
        group_streams: 80,
        private_streams: 48
      },
      plugins: {
        loaded_count: 12,
        failed_count: 1
      },
      components: {
        total_count: 45,
        enabled_count: 40
      }
    }
  },

  // 日程
  schedule: {
    success: true,
    data: {
      date: '2025年12月20日',
      current_activity: {
        time_range: '14:00 - 16:00',
        activity: '代码开发'
      },
      activities: [
        { time_range: '09:00 - 10:00', activity: '晨会' },
        { time_range: '10:00 - 12:00', activity: '需求分析' },
        { time_range: '12:00 - 14:00', activity: '午休' },
        { time_range: '14:00 - 16:00', activity: '代码开发' },
        { time_range: '16:00 - 18:00', activity: '代码审查' }
      ]
    }
  },

  // 月度计划
  monthlyPlans: {
    success: true,
    data: {
      total: 5,
      plans: [
        '完成 WebUI 重构',
        '优化插件加载速度',
        '发布 v2.0 版本',
        '撰写开发文档',
        '社区活动组织'
      ]
    }
  },

  // LLM 统计
  llmStats: {
    success: true,
    data: {
      total_requests: 1500,
      total_tokens: 2500000,
      cost: 12.5
    }
  },

  // 消息统计
  messageStats: {
    success: true,
    data: {
      data_points: Array.from({ length: 24 }, (_, i) => ({
        timestamp: `${i}:00`,
        received: Math.floor(Math.random() * 100),
        sent: Math.floor(Math.random() * 100)
      }))
    }
  },

  // 插件列表
  plugins: {
    success: true,
    data: {
      loaded: [
        { id: 'plugin-1', name: '基础指令插件', version: '1.0.0', author: 'MoFox Team', description: '提供基础的机器人指令', enabled: true },
        { id: 'plugin-2', name: 'AI 对话插件', version: '2.1.0', author: 'MoFox Team', description: '集成 LLM 进行智能对话', enabled: true },
        { id: 'plugin-3', name: '定时任务插件', version: '1.2.0', author: 'Community', description: '管理定时任务', enabled: true },
        { id: 'plugin-4', name: '天气查询', version: '1.0.1', author: 'User123', description: '查询各地天气', enabled: false },
      ],
      failed: [
        { id: 'plugin-5', name: '损坏的插件', version: '0.0.1', author: 'Unknown', description: '加载失败示例', error: 'ImportError: missing module' }
      ]
    }
  },

  // 组件列表
  components: {
    success: true,
    data: {
      components: [
        { id: 'comp-1', name: 'EchoHandler', type: 'handler', description: '回显消息', enabled: true, plugin_id: 'plugin-1' },
        { id: 'comp-2', name: 'ChatGenerator', type: 'generator', description: '生成回复', enabled: true, plugin_id: 'plugin-2' },
        { id: 'comp-3', name: 'DailyReport', type: 'scheduled_task', description: '每日汇报', enabled: true, plugin_id: 'plugin-3' },
        { id: 'comp-4', name: 'WeatherTool', type: 'tool', description: '获取天气信息', enabled: false, plugin_id: 'plugin-4' },
      ]
    }
  },

  // 日志
  logs: {
    success: true,
    data: {
      logs: [
        { timestamp: '2025-12-20 14:30:01', level: 'INFO', logger: 'Core', message: '系统运行正常' },
        { timestamp: '2025-12-20 14:30:05', level: 'DEBUG', logger: 'PluginManager', message: '正在加载插件...' },
        { timestamp: '2025-12-20 14:30:10', level: 'WARNING', logger: 'Network', message: '连接延迟较高' },
        { timestamp: '2025-12-20 14:30:15', level: 'ERROR', logger: 'Plugin-5', message: '插件加载失败: ImportError' }
      ]
    }
  },
  
  // 默认成功响应
  success: {
    success: true,
    data: { success: true }
  }
}
