# MoFox-Bot Web管理界面 - 仪表盘设计分析

## 项目背景

MoFox-Bot 是一个基于 MaiCore 的 AI 智能体，具有丰富的功能模块和数据统计能力。本文档分析了项目结构，并为 Web 管理界面提供设计建议。

## 一、项目核心功能分析

### 1. Bot核心系统
- **多平台支持**: QQ、私聊、群聊等多种聊天场景
- **插件系统**: 支持动态加载和管理插件
- **人格系统**: 可配置的AI人格和表达风格
- **记忆系统**: 三层记忆架构（感知、短期、长期）
- **情绪系统**: 情感表达和表情包管理

### 2. 数据统计维度（从 local_store.json 分析）

#### 2.1 API调用统计
- **总请求数**: total_requests
- **请求类型分布**: schedule, interest_embedding, interest_generation 等
- **按用户统计**: requests_by_user
- **按模型统计**: requests_by_model
- **按模块统计**: requests_by_module
- **按提供商统计**: requests_by_provider

#### 2.2 Token使用统计
- **输入Token**: in_tokens (按类型/用户/模型/模块分类)
- **输出Token**: out_tokens (按类型/用户/模型/模块分类)
- **总Token消耗**: tokens_by_type/user/model/module/provider

#### 2.3 成本统计
- **总成本**: total_cost
- **按类型/用户/模型/模块分类的成本**
- **每千Token成本**: cost_per_ktok_by_model
- **按提供商成本分布**: costs_by_provider

#### 2.4 性能指标
- **响应时间**: time_costs (按类型/用户/模型/模块/提供商)
- **平均响应时间**: avg_time_costs
- **响应时间标准差**: std_time_costs
- **TPS (每秒Token数)**: tps_by_model, tps_by_provider
- **平均Token数**: avg_tok_by_model

#### 2.5 系统运行状态
- **在线时长**: online_time
- **部署时间**: deploy_time
- **总消息数**: total_messages
- **按聊天分类的消息**: messages_by_chat

## 二、仪表盘功能模块设计

### 1. 核心统计卡片 (顶部)
- ✅ **总请求数**: 显示API总调用次数
- ✅ **在线时长**: 从部署时间计算运行时长
- ✅ **Token消耗**: 总Token数（输入+输出）
- ✅ **API成本**: 总花费金额

### 2. 主要可视化图表

#### 2.1 趋势分析 (左侧大图)
- **API调用趋势图**: 时间序列折线图
  - X轴: 时间
  - Y轴: 请求数/响应时间/Token消耗
  - 多条线对比不同指标
  
#### 2.2 分布分析 (饼图/环形图)
- **请求类型分布**: requests_by_type
- **模型使用分布**: requests_by_model
- **模块调用分布**: requests_by_module
- **提供商分布**: requests_by_provider
- **成本分布**: costs_by_module

#### 2.3 性能对比 (条形图)
- **模型响应时间对比**: bar_chart_avg_response_time
- **Token输入输出对比**: bar_chart_token_comparison
- **模型请求量对比**: bar_chart_req_by_model

#### 2.4 散点分析
- **响应时间散点图**: scatter_chart_response_time
  - 可以看出响应时间与Token数的关系
  
#### 2.5 雷达图
- **模型效率雷达图**: radar_chart_model_efficiency
  - 维度: 请求量、TPS、响应速度、成本效益、Token容量

### 3. 系统状态监控 (右侧边栏)
- ✅ **Bot在线状态**: 运行/停止
- ✅ **数据库类型**: SQLite/MySQL/PostgreSQL
- ✅ **功能模块状态**:
  - 记忆系统 (enable_memory)
  - 表情包系统 (emoji_chance)
  - 插件系统 (enable_tool)
  - 情绪系统 (enable_mood)
  - 联网搜索 (enable_web_search_tool)
  - 视频分析 (enable_video_analysis)
  - 主动思考 (proactive_thinking.enable)
  - 日程系统 (schedule_enable)

### 4. 详细数据表格

#### 4.1 模型使用统计表
- 模型名称
- 请求次数
- 平均TPS
- 平均响应时间
- Token消耗
- 成本

#### 4.2 插件状态表
- 插件名称
- 运行状态
- 调用次数
- 最后活跃时间

#### 4.3 聊天活动表
- 聊天ID
- 平台
- 消息数量
- 最后活跃时间

### 5. 性能监控面板
- **实时性能指标**:
  - 平均响应时间
  - 内存使用 (需要添加)
  - CPU使用率 (需要添加)
  - 活跃聊天流数量
  
- **告警指标**:
  - 异常响应时间
  - 高成本告警
  - 系统资源告警

## 三、数据接口设计建议

### 3.1 实时统计接口
```
GET /api/stats/summary
返回: 核心统计数据（请求数、时长、Token、成本）

GET /api/stats/timeline
返回: 时间序列数据（用于趋势图）

GET /api/stats/models
返回: 模型详细统计

GET /api/stats/plugins
返回: 插件状态和统计
```

### 3.2 系统状态接口
```
GET /api/system/status
返回: 系统各模块状态

GET /api/system/config
返回: 配置信息（从bot_config.toml读取）

POST /api/system/control
请求: 启动/停止/重启等控制命令
```

### 3.3 聊天数据接口
```
GET /api/chats/list
返回: 聊天列表

GET /api/chats/{chat_id}/messages
返回: 特定聊天的消息历史

GET /api/chats/{chat_id}/stats
返回: 特定聊天的统计数据
```

## 四、UI/UX设计要点

### 4.1 设计风格
- ✅ **像素风格**: 使用 Press Start 2P 字体
- ✅ **色彩方案**:
  - 主色: 蓝色 (#4A90E2)
  - 辅色: 浅蓝色 (#7DB5EC, #B8D9F5)
  - 背景: 白色和浅灰色
  - 状态色: 绿色(成功)、黄色(警告)、红色(错误)

### 4.2 布局结构
- **顶部导航栏**: Logo、用户信息、系统状态
- **统计卡片区**: 4个关键指标卡片
- **主内容区**: 左侧大图表 + 右侧系统状态
- **详细数据区**: 多个卡片式模块

### 4.3 交互设计
- **实时更新**: WebSocket连接实时更新数据
- **可配置仪表盘**: 允许用户自定义显示模块
- **响应式设计**: 适配移动端和桌面端
- **主题切换**: 支持明暗主题

## 五、技术栈建议

### 前端框架
- **Vue 3**: 使用 Composition API
- **Vite**: 构建工具
- **TypeScript**: 类型安全

### UI组件库
- **Element Plus**: 提供基础组件
- **ECharts**: 图表库（支持多种图表类型）
- **Tailwind CSS**: 实用工具类CSS

### 状态管理
- **Pinia**: Vue 3官方推荐状态管理
- **VueUse**: 常用组合式API工具集

### 通信方案
- **Axios**: HTTP请求
- **Socket.IO**: WebSocket实时通信

## 六、开发优先级

### Phase 1: 核心功能 (MVP)
1. ✅ 登录页面
2. ✅ 仪表盘框架
3. ✅ 核心统计卡片
4. ✅ 系统状态显示
5. 基础图表展示

### Phase 2: 增强功能
1. 实时数据更新
2. 详细数据表格
3. 更多图表类型
4. 筛选和搜索功能

### Phase 3: 高级功能
1. 配置管理界面
2. 插件管理
3. 日志查看
4. 系统控制（启动/停止）
5. 告警和通知

## 七、数据展示优化建议

### 7.1 性能优化
- 虚拟滚动: 处理大量数据
- 懒加载: 按需加载图表
- 数据缓存: 减少API请求

### 7.2 可视化优化
- 图表响应式: 自适应不同屏幕尺寸
- 动画效果: 平滑的数据更新动画
- 颜色编码: 统一的状态颜色方案

### 7.3 用户体验
- 加载状态: 骨架屏或加载动画
- 错误处理: 友好的错误提示
- 数据导出: 支持导出统计报表

## 八、安全性考虑

1. **身份验证**: JWT Token + 会话管理
2. **权限控制**: 基于角色的访问控制
3. **数据加密**: HTTPS + 敏感数据加密
4. **CSRF防护**: CSRF Token验证
5. **XSS防护**: 输入验证和输出转义

## 总结

MoFox-Bot 拥有丰富的统计数据和功能模块，可以打造一个功能强大的管理仪表盘。建议采用渐进式开发策略，先完成核心功能，再逐步添加增强功能。重点关注数据可视化、实时性和用户体验。
