# MoFox WebUI 插件管理系统设计文档

## 📋 目录
- [概述](#概述)
- [功能模块](#功能模块)
- [后端设计](#后端设计)
- [前端设计](#前端设计)
- [API接口](#api接口)
- [数据模型](#数据模型)
- [实现计划](#实现计划)

---

## 概述

### 设计目标
为 MoFox WebUI 添加完整的插件管理功能，包括：
1. **本地插件管理**（第一阶段）：查看、启用/禁用、加载/卸载、重载插件
2. **网络插件管理**（第二阶段）：浏览、搜索、下载、安装网络上的插件

### 架构概览
```
┌─────────────────────────────────────────────────────────┐
│                    前端 Vue 界面                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 插件列表视图 │  │ 插件详情视图 │  │ 插件商店视图 │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP API
┌─────────────────────────────────────────────────────────┐
│              后端 FastAPI Router 组件                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │         WebUIPluginRouter (新增)                  │  │
│  │  - 本地插件管理 API                               │  │
│  │  - 网络插件管理 API (预留)                        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ 调用
┌─────────────────────────────────────────────────────────┐
│            Plugin System Core (现有)                     │
│  - plugin_manage_api                                    │
│  - plugin_info_api                                      │
│  - component_state_api                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 功能模块

### 第一阶段：本地插件管理

#### 1. 插件列表展示
**功能描述**：
- 以表格或卡片形式展示所有插件
- 支持按状态筛选（已加载/已注册/失败）
- 显示插件基本信息和状态

**展示信息**：
- 插件名称（中文显示名 + 英文标识）
- 版本号
- 作者
- 描述
- 启用/禁用状态
- 加载状态（已加载/未加载/加载失败）
- 组件数量
- 最后更新时间

**交互功能**：
- 点击查看详情
- 快速启用/禁用开关
- 批量操作（启用/禁用/重载）
- 搜索和过滤

#### 2. 插件详情页
**功能描述**：
- 展示插件完整信息
- 查看插件包含的所有组件
- 管理插件状态

**展示内容**：
- **基本信息**：名称、版本、作者、描述、主页链接
- **状态信息**：启用状态、加载状态、依赖关系
- **组件列表**：
  - 按类型分组（Command/Action/EventHandler/Router/Tool等）
  - 每个组件的名称、描述、启用状态
  - 组件级别的启用/禁用控制
- **配置管理**：
  - 跳转到插件配置页面
  - 显示配置文件路径
- **日志查看**：
  - 查看插件相关日志
  - 过滤错误和警告

**操作功能**：
- 启用/禁用插件
- 重载插件
- 卸载插件（确认对话框）
- 查看配置
- 查看组件详情

#### 3. 插件操作功能

##### 3.1 启用/禁用
- 一键切换插件启用状态
- 禁用不会卸载，只是停止功能
- 批量操作支持

##### 3.2 加载/卸载
- 加载：将已注册但未加载的插件加载到内存
- 卸载：从内存中完全移除插件
- 提供确认对话框防止误操作

##### 3.3 重载插件
- 热重载单个插件
- 热重载所有插件
- 显示重载进度和结果

##### 3.4 扫描新插件
- 重新扫描插件目录
- 自动注册新发现的插件
- 可选择是否立即加载

##### 3.5 组件管理
- 查看插件的所有组件
- 单独启用/禁用某个组件
- 查看组件依赖关系

#### 4. 插件状态监控
**功能描述**：
- 实时显示插件运行状态
- 监控异常和错误

**监控内容**：
- 加载失败的插件及错误原因
- 组件注册失败信息
- 依赖缺失警告
- 性能指标（可选）

---

### 第二阶段：网络插件管理（预留）

#### 1. 插件商店
- 浏览所有可用插件
- 搜索和过滤
- 查看插件详情、评分、下载量

#### 2. 插件下载与安装
- 从仓库下载插件
- 自动处理依赖
- 安装进度显示

#### 3. 插件更新
- 检查插件更新
- 一键更新
- 批量更新

---

## 后端设计

### 新增路由组件：WebUIPluginRouter

**文件位置**：`backend/routers/plugin_router.py`

#### 类结构
```python
class WebUIPluginRouter(BaseRouterComponent):
    """插件管理路由组件"""
    component_name = "plugin_manager"
    component_description = "提供插件管理API接口"
    component_version = "1.0.0"
```

#### 核心功能模块

##### 1. 插件列表与查询
- `GET /plugins` - 获取所有插件列表
- `GET /plugins/{plugin_name}` - 获取单个插件详情
- `GET /plugins/by-status` - 按状态分组获取插件
- `GET /plugins/search` - 搜索插件

##### 2. 插件状态管理
- `POST /plugins/{plugin_name}/enable` - 启用插件
- `POST /plugins/{plugin_name}/disable` - 禁用插件
- `GET /plugins/{plugin_name}/status` - 获取插件状态

##### 3. 插件生命周期管理
- `POST /plugins/{plugin_name}/load` - 加载插件
- `POST /plugins/{plugin_name}/unload` - 卸载插件
- `POST /plugins/{plugin_name}/reload` - 重载插件
- `POST /plugins/reload-all` - 重载所有插件

##### 4. 插件扫描与注册
- `POST /plugins/scan` - 扫描插件目录
- `POST /plugins/register` - 注册指定插件

##### 5. 组件管理
- `GET /plugins/{plugin_name}/components` - 获取插件的所有组件
- `POST /plugins/{plugin_name}/components/{component_name}/enable` - 启用组件
- `POST /plugins/{plugin_name}/components/{component_name}/disable` - 禁用组件
- `GET /plugins/{plugin_name}/components/{component_name}` - 获取组件详情

##### 6. 批量操作
- `POST /plugins/batch/enable` - 批量启用
- `POST /plugins/batch/disable` - 批量禁用
- `POST /plugins/batch/reload` - 批量重载

#### API 实现要点

1. **调用现有 API**：
   ```python
   from src.plugin_system.apis import (
       plugin_manage_api,
       plugin_info_api,
       component_state_api
   )
   ```

2. **错误处理**：
   - 统一的错误响应格式
   - 详细的错误信息
   - 合适的 HTTP 状态码

3. **权限验证**：
   - 所有接口需要 `VerifiedDep` 身份验证
   - 敏感操作（卸载、批量操作）需要额外确认

4. **异步操作**：
   - 耗时操作使用异步处理
   - 提供操作进度反馈
   - 支持任务取消（可选）

---

## 前端设计

### 新增页面组件

#### 1. PluginManageView.vue
**路径**：`/dashboard/plugin-manage`

**功能**：插件管理主页面

**布局结构**：
```
┌─────────────────────────────────────────────┐
│ 标题栏：插件管理                             │
│ 操作按钮：[刷新] [扫描新插件] [批量操作]      │
├─────────────────────────────────────────────┤
│ 筛选栏：                                     │
│ [全部|已加载|已注册|失败] [搜索框]           │
├─────────────────────────────────────────────┤
│ 统计卡片：                                   │
│ [已加载:X] [已启用:X] [失败:X] [总计:X]     │
├─────────────────────────────────────────────┤
│ 插件列表：                                   │
│ ┌──────────────────────────────────────┐   │
│ │ 🔌 插件名称          版本  作者      │   │
│ │    描述信息                           │   │
│ │    [●启用] [已加载] 3个组件           │   │
│ │    [详情] [重载] [配置]               │   │
│ ├──────────────────────────────────────┤   │
│ │ ... 更多插件 ...                     │   │
│ └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**核心功能**：
- 插件列表展示（表格或卡片视图）
- 状态筛选和搜索
- 快速操作（启用/禁用/重载）
- 跳转到详情页

#### 2. PluginDetailView.vue
**路径**：`/dashboard/plugin-manage/:pluginName`

**功能**：插件详情和深度管理

**布局结构**：
```
┌─────────────────────────────────────────────┐
│ [← 返回]  插件名称                           │
│ 版本 | 作者 | [启用开关] [重载] [卸载]        │
├─────────────────────────────────────────────┤
│ Tab 导航：[概览] [组件] [配置] [日志]        │
├─────────────────────────────────────────────┤
│                                              │
│ 概览 Tab:                                    │
│   基本信息、描述、主页链接等                  │
│                                              │
│ 组件 Tab:                                    │
│   ┌─ Command (5) ───────────────────┐      │
│   │ command_1  [●启用]  描述         │      │
│   │ command_2  [○禁用]  描述         │      │
│   └─────────────────────────────────┘      │
│   ┌─ EventHandler (3) ──────────────┐      │
│   │ ...                             │      │
│   └─────────────────────────────────┘      │
│                                              │
│ 配置 Tab:                                    │
│   配置文件路径、快捷跳转                      │
│                                              │
│ 日志 Tab:                                    │
│   插件相关日志（过滤显示）                    │
│                                              │
└─────────────────────────────────────────────┘
```

**核心功能**：
- 多 Tab 展示详细信息
- 组件树形列表
- 组件级别启用/禁用
- 配置文件跳转
- 实时日志查看

#### 3. 组件更新

##### Sidebar.vue 更新
在导航菜单中添加"插件管理"项：
```typescript
const menuItems = [
  { name: '仪表盘', path: '/dashboard', icon: 'lucide:layout-dashboard' },
  { 
    name: '配置管理', 
    path: '/dashboard/config', 
    icon: 'lucide:settings',
    key: 'config',
    children: [
      { name: '机器人配置', path: '/dashboard/bot-config', icon: 'lucide:bot' },
      { name: '模型配置', path: '/dashboard/model-config', icon: 'lucide:brain' },
      { name: '插件配置', path: '/dashboard/plugin-config', icon: 'lucide:puzzle' },
    ]
  },
  // 新增：插件管理
  { 
    name: '插件管理', 
    path: '/dashboard/plugin-manage', 
    icon: 'lucide:package', 
  },
]
```

### 状态管理

创建 `stores/plugin.ts`：
```typescript
export const usePluginStore = defineStore('plugin', {
  state: () => ({
    plugins: [] as Plugin[],
    currentPlugin: null as Plugin | null,
    loading: false,
    error: null as string | null,
  }),
  
  actions: {
    async fetchPlugins() { ... },
    async fetchPluginDetail(name: string) { ... },
    async enablePlugin(name: string) { ... },
    async disablePlugin(name: string) { ... },
    async reloadPlugin(name: string) { ... },
    async unloadPlugin(name: string) { ... },
    async scanPlugins() { ... },
  }
})
```

### API 客户端

在 `api/index.ts` 中添加插件管理相关接口：
```typescript
// API 端点
const API_ENDPOINTS = {
  // ... 现有端点 ...
  PLUGIN: {
    LIST: '/plugin-api/webui_auth/plugin_manager/plugins',
    DETAIL: (name: string) => `/plugin-api/webui_auth/plugin_manager/plugins/${name}`,
    ENABLE: (name: string) => `/plugin-api/webui_auth/plugin_manager/plugins/${name}/enable`,
    DISABLE: (name: string) => `/plugin-api/webui_auth/plugin_manager/plugins/${name}/disable`,
    RELOAD: (name: string) => `/plugin-api/webui_auth/plugin_manager/plugins/${name}/reload`,
    UNLOAD: (name: string) => `/plugin-api/webui_auth/plugin_manager/plugins/${name}/unload`,
    SCAN: '/plugin-api/webui_auth/plugin_manager/plugins/scan',
    COMPONENTS: (name: string) => `/plugin-api/webui_auth/plugin_manager/plugins/${name}/components`,
  }
}
```

---

## API 接口

### 1. 获取插件列表

**请求**：
```http
GET /plugin-api/webui_auth/plugin_manager/plugins
```

**响应**：
```json
{
  "success": true,
  "plugins": [
    {
      "name": "example_plugin",
      "display_name": "示例插件",
      "version": "1.0.0",
      "author": "作者",
      "description": "插件描述",
      "enabled": true,
      "loaded": true,
      "components_count": 5,
      "last_updated": "2024-01-01T00:00:00Z",
      "config_path": "config/plugins/example_plugin.toml"
    }
  ],
  "total": 10,
  "loaded": 8,
  "enabled": 7,
  "failed": 2
}
```

### 2. 获取插件详情

**请求**：
```http
GET /plugin-api/webui_auth/plugin_manager/plugins/{plugin_name}
```

**响应**：
```json
{
  "success": true,
  "plugin": {
    "name": "example_plugin",
    "display_name": "示例插件",
    "version": "1.0.0",
    "author": "作者",
    "description": "插件描述",
    "enabled": true,
    "loaded": true,
    "components": [
      {
        "name": "example_command",
        "type": "Command",
        "description": "示例命令",
        "enabled": true
      },
      {
        "name": "example_router",
        "type": "Router",
        "description": "HTTP路由",
        "enabled": true
      }
    ],
    "config": {
      "path": "config/plugins/example_plugin.toml",
      "exists": true
    },
    "metadata": {
      "homepage": "https://example.com",
      "repository": "https://github.com/example/plugin",
      "dependencies": ["dependency1", "dependency2"]
    }
  }
}
```

### 3. 启用插件

**请求**：
```http
POST /plugin-api/webui_auth/plugin_manager/plugins/{plugin_name}/enable
```

**响应**：
```json
{
  "success": true,
  "message": "插件已启用"
}
```

### 4. 禁用插件

**请求**：
```http
POST /plugin-api/webui_auth/plugin_manager/plugins/{plugin_name}/disable
```

**响应**：
```json
{
  "success": true,
  "message": "插件已禁用"
}
```

### 5. 重载插件

**请求**：
```http
POST /plugin-api/webui_auth/plugin_manager/plugins/{plugin_name}/reload
```

**响应**：
```json
{
  "success": true,
  "message": "插件重载成功"
}
```

### 6. 卸载插件

**请求**：
```http
POST /plugin-api/webui_auth/plugin_manager/plugins/{plugin_name}/unload
```

**响应**：
```json
{
  "success": true,
  "message": "插件已卸载"
}
```

### 7. 扫描新插件

**请求**：
```http
POST /plugin-api/webui_auth/plugin_manager/plugins/scan
Content-Type: application/json

{
  "load_after_register": true
}
```

**响应**：
```json
{
  "success": true,
  "registered": 3,
  "loaded": 2,
  "failed": 0,
  "new_plugins": ["plugin1", "plugin2"]
}
```

### 8. 获取插件组件

**请求**：
```http
GET /plugin-api/webui_auth/plugin_manager/plugins/{plugin_name}/components
```

**响应**：
```json
{
  "success": true,
  "plugin_name": "example_plugin",
  "components": [
    {
      "name": "example_command",
      "type": "Command",
      "description": "示例命令",
      "enabled": true,
      "details": {
        "triggers": ["!example", "/example"],
        "permission_required": "user"
      }
    }
  ],
  "total": 5,
  "enabled": 4,
  "disabled": 1
}
```

### 9. 启用/禁用组件

**请求**：
```http
POST /plugin-api/webui_auth/plugin_manager/plugins/{plugin_name}/components/{component_name}/enable
POST /plugin-api/webui_auth/plugin_manager/plugins/{plugin_name}/components/{component_name}/disable
```

**响应**：
```json
{
  "success": true,
  "message": "组件状态已更新"
}
```

### 10. 批量操作

**请求**：
```http
POST /plugin-api/webui_auth/plugin_manager/plugins/batch/enable
Content-Type: application/json

{
  "plugin_names": ["plugin1", "plugin2", "plugin3"]
}
```

**响应**：
```json
{
  "success": true,
  "results": {
    "plugin1": {"success": true, "message": "已启用"},
    "plugin2": {"success": true, "message": "已启用"},
    "plugin3": {"success": false, "error": "插件不存在"}
  },
  "total": 3,
  "succeeded": 2,
  "failed": 1
}
```

---

## 数据模型

### 后端 Pydantic 模型

```python
# ==================== 响应模型 ====================

class PluginItemResponse(BaseModel):
    """插件列表项"""
    name: str
    display_name: str
    version: str
    author: str
    description: Optional[str] = None
    enabled: bool
    loaded: bool
    components_count: int
    last_updated: Optional[str] = None
    config_path: Optional[str] = None
    error: Optional[str] = None

class PluginListResponse(BaseModel):
    """插件列表响应"""
    success: bool
    plugins: list[PluginItemResponse]
    total: int
    loaded: int
    enabled: int
    failed: int
    error: Optional[str] = None

class ComponentItemResponse(BaseModel):
    """组件项"""
    name: str
    type: str
    description: Optional[str] = None
    enabled: bool
    details: Optional[dict] = None

class PluginDetailResponse(BaseModel):
    """插件详情响应"""
    success: bool
    plugin: Optional[dict] = None
    error: Optional[str] = None

class OperationResponse(BaseModel):
    """操作响应"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None

class ScanResultResponse(BaseModel):
    """扫描结果响应"""
    success: bool
    registered: int
    loaded: int
    failed: int
    new_plugins: list[str]
    error: Optional[str] = None

class BatchOperationResponse(BaseModel):
    """批量操作响应"""
    success: bool
    results: dict[str, dict]
    total: int
    succeeded: int
    failed: int

# ==================== 请求模型 ====================

class ScanRequest(BaseModel):
    """扫描请求"""
    load_after_register: bool = True

class BatchOperationRequest(BaseModel):
    """批量操作请求"""
    plugin_names: list[str]
```

### 前端 TypeScript 类型

```typescript
// ==================== 基础类型 ====================

export interface Plugin {
  name: string
  display_name: string
  version: string
  author: string
  description?: string
  enabled: boolean
  loaded: boolean
  components_count: number
  last_updated?: string
  config_path?: string
  error?: string
}

export interface PluginListResponse {
  success: boolean
  plugins: Plugin[]
  total: number
  loaded: number
  enabled: number
  failed: number
  error?: string
}

export interface Component {
  name: string
  type: string
  description?: string
  enabled: boolean
  details?: Record<string, any>
}

export interface PluginDetail extends Plugin {
  components: Component[]
  config: {
    path: string
    exists: boolean
  }
  metadata?: {
    homepage?: string
    repository?: string
    dependencies?: string[]
  }
}

export interface PluginDetailResponse {
  success: boolean
  plugin?: PluginDetail
  error?: string
}

export interface OperationResponse {
  success: boolean
  message?: string
  error?: string
}

export interface ScanResult {
  success: boolean
  registered: number
  loaded: number
  failed: number
  new_plugins: string[]
  error?: string
}

export interface BatchOperationResult {
  success: boolean
  results: Record<string, { success: boolean; message?: string; error?: string }>
  total: number
  succeeded: number
  failed: number
}
```

---

## 实现计划

### 阶段 1：后端基础（1-2天）

#### 步骤 1.1：创建路由组件骨架
- [ ] 创建 `backend/routers/plugin_router.py`
- [ ] 实现 `WebUIPluginRouter` 基础类
- [ ] 定义所有响应和请求模型
- [ ] 在 `plugin.py` 中注册新路由

#### 步骤 1.2：实现核心 API
- [ ] 实现插件列表接口
- [ ] 实现插件详情接口
- [ ] 实现启用/禁用接口
- [ ] 实现加载/卸载/重载接口

#### 步骤 1.3：实现高级功能
- [ ] 实现扫描插件接口
- [ ] 实现组件查询接口
- [ ] 实现组件状态管理接口
- [ ] 实现批量操作接口

#### 步骤 1.4：测试后端
- [ ] 使用 Postman/Insomnia 测试所有接口
- [ ] 验证错误处理
- [ ] 验证权限控制

### 阶段 2：前端基础（2-3天）

#### 步骤 2.1：创建基础结构
- [ ] 创建 `stores/plugin.ts` 状态管理
- [ ] 在 `api/index.ts` 中添加 API 客户端方法
- [ ] 定义 TypeScript 类型

#### 步骤 2.2：实现插件列表页
- [ ] 创建 `PluginManageView.vue`
- [ ] 实现插件列表展示（表格/卡片）
- [ ] 实现筛选和搜索功能
- [ ] 实现快速操作（启用/禁用/重载）

#### 步骤 2.3：实现插件详情页
- [ ] 创建 `PluginDetailView.vue`
- [ ] 实现多 Tab 布局
- [ ] 实现概览 Tab
- [ ] 实现组件 Tab
- [ ] 实现配置和日志 Tab（链接）

#### 步骤 2.4：完善交互
- [ ] 添加确认对话框（卸载等危险操作）
- [ ] 添加加载动画
- [ ] 添加 Toast 提示
- [ ] 优化错误处理和用户反馈

#### 步骤 2.5：集成到主应用
- [ ] 在 `router/index.ts` 中添加路由
- [ ] 在 `Sidebar.vue` 中添加菜单项
- [ ] 测试路由跳转和状态同步

### 阶段 3：优化和完善（1-2天）

#### 步骤 3.1：UI/UX 优化
- [ ] 统一样式和主题
- [ ] 添加动画效果
- [ ] 优化响应式布局
- [ ] 提升加载性能

#### 步骤 3.2：功能增强
- [ ] 添加批量操作 UI
- [ ] 添加插件搜索建议
- [ ] 添加操作历史记录
- [ ] 添加快捷键支持

#### 步骤 3.3：测试和修复
- [ ] 功能测试
- [ ] 边界情况测试
- [ ] 错误处理测试
- [ ] 性能测试

### 阶段 4：文档和发布（0.5-1天）

- [ ] 编写用户文档
- [ ] 编写开发者文档
- [ ] 更新 README
- [ ] 准备发布说明

---

## 技术要点

### 后端要点

1. **复用现有 API**
   - 充分利用 `plugin_manage_api`、`plugin_info_api`、`component_state_api`
   - 避免重复实现底层逻辑

2. **错误处理**
   ```python
   try:
       result = await plugin_manage_api.enable_plugin(plugin_name)
       return OperationResponse(success=True, message="插件已启用")
   except ValueError as e:
       return OperationResponse(success=False, error=str(e))
   except Exception as e:
       logger.error(f"启用插件失败: {e}", exc_info=True)
       return OperationResponse(success=False, error="内部错误")
   ```

3. **异步处理**
   - 使用 `async/await` 处理耗时操作
   - 考虑添加后台任务支持

4. **权限控制**
   - 所有接口使用 `VerifiedDep` 验证身份
   - 考虑添加角色权限控制

### 前端要点

1. **状态管理**
   - 使用 Pinia 集中管理插件状态
   - 避免冗余的 API 调用

2. **用户体验**
   - 操作前确认（卸载等危险操作）
   - 加载状态反馈
   - 操作结果提示
   - 错误信息友好展示

3. **性能优化**
   - 列表虚拟滚动（插件数量多时）
   - 懒加载详情数据
   - 防抖搜索输入

4. **样式一致性**
   - 复用现有组件样式
   - 遵循 Material Design 3 规范
   - 支持亮色/暗色主题

---

## 安全考虑

1. **身份验证**
   - 所有 API 需要 token 验证
   - Token 过期处理

2. **操作权限**
   - 危险操作（卸载、批量操作）需要二次确认
   - 考虑添加操作审计日志

3. **输入验证**
   - 插件名称验证（防止路径遍历）
   - 参数类型和范围检查

4. **错误信息**
   - 不暴露敏感路径信息
   - 统一的错误响应格式

---

## 未来扩展

### 短期（第二阶段）
- [ ] 插件商店集成
- [ ] 插件下载和安装
- [ ] 插件依赖管理
- [ ] 插件更新检查

### 中期
- [ ] 插件开发工具（脚手架）
- [ ] 插件测试环境
- [ ] 插件性能分析
- [ ] 插件市场评分系统

### 长期
- [ ] 插件沙箱隔离
- [ ] 插件热更新（无需重启）
- [ ] 插件协作功能
- [ ] 插件可视化编辑器

---

## 总结

本设计文档提供了完整的 MoFox WebUI 插件管理系统实现方案，分为两个阶段：

**第一阶段（本地插件管理）** 专注于：
- 插件列表展示和搜索
- 插件启用/禁用/重载/卸载
- 插件详情和组件管理
- 插件扫描和注册

**第二阶段（网络插件管理）** 将实现：
- 插件商店浏览
- 插件下载和安装
- 插件更新管理

预计总开发时间：**5-7天**（第一阶段）

本设计充分复用现有的插件系统 API，保证了架构的一致性和可维护性。前后端分离的设计使得功能模块清晰，便于团队协作和后续扩展。
