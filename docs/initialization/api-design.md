# 后端 API 设计

> 本文档描述初始化系统所需的所有后端 API 端点

---

## 📋 API 端点列表

所有初始化相关的 API 端点注册在 `/api/initialization/*` 路径下。

### 端点概览

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/api/initialization/status` | GET | 检查初始化状态 | ✅ |
| `/api/initialization/save-bot-config` | POST | 保存机器人配置 | ✅ |
| `/api/initialization/save-model-config` | POST | 保存模型配置 | ✅ |
| `/api/initialization/save-git-config` | POST | 保存 Git 配置 | ✅ |
| `/api/initialization/test-model` | POST | 测试模型连接 | ✅ |
| `/api/initialization/detect-git` | POST | 检测 Git 路径 | ✅ |
| `/api/initialization/complete` | POST | 标记初始化完成 | ✅ |

---

## 🔍 1. 检查初始化状态

### GET `/api/initialization/status`

**功能**: 检查系统初始化状态和各步骤配置情况

**请求**: 无请求体

**响应**:
```json
{
  "success": true,
  "data": {
    "initialized": false,
    "initialized_at": null,
    "steps": {
      "bot_config": {
        "completed": false,
        "has_existing": false,
        "details": null
      },
      "model_config": {
        "completed": false,
        "has_existing": false,
        "providers": [],
        "details": null
      },
      "git_config": {
        "completed": true,
        "has_existing": true,
        "git_detected": true,
        "git_version": "2.43.0",
        "git_path": "C:\\Program Files\\Git\\bin\\git.exe",
        "source": "system"
      }
    }
  }
}
```

**字段说明**:
- `initialized`: 是否已完成初始化
- `initialized_at`: 初始化完成时间 (ISO 8601 格式)
- `steps.{step}.completed`: 该步骤是否已完成
- `steps.{step}.has_existing`: 是否存在现有配置
- `steps.{step}.details`: 现有配置的摘要信息

---

## 💾 2. 保存机器人配置

### POST `/api/initialization/save-bot-config`

**功能**: 保存机器人的基础配置（昵称、人格、Master用户等）

**请求体**:
```json
{
  "bot_name": "墨狐",
  "personality_core": "是一个积极向上的女大学生",
  "personality_side": "用一句话或几句话描述人格的侧面特质",
  "identity": "年龄为19岁,是女孩子,身高为160cm,有黑色的短发",
  "reply_style": "回复可以简短一些。可以参考贴吧，知乎和微博的回复风格，回复不要浮夸，不要用夸张修辞，平淡一些。",
  "master_users": [
    ["qq", "123456789"],
    ["telegram", "user_abc"]
  ]
}
```

**字段说明**:
- `bot_name` (必填): 机器人昵称
- `personality_core` (必填): 核心人格描述
- `personality_side` (可选): 人格侧面描述
- `identity` (可选): 身份描述
- `reply_style` (可选): 回复风格
- `master_users` (必填): Master用户列表，格式 `[[平台, 用户ID], ...]`

**响应**:
```json
{
  "success": true,
  "message": "机器人配置已保存",
  "backup_path": "config/backups/bot_config_20250127_143022.toml"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "master_users 不能为空"
}
```

---

## 🧠 3. 保存模型配置

### POST `/api/initialization/save-model-config`

**功能**: 保存 SiliconFlow API 配置

**请求体**:
```json
{
  "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
}
```

**响应**:
```json
{
  "success": true,
  "message": "模型配置已保存"
}
```

**实现要点**:
- 自动配置 SiliconFlow provider
- 自动添加 DeepSeek-V3 作为默认模型
- 配置到 `config/model_config.toml`

---

## 🔧 4. 保存 Git 配置

### POST `/api/initialization/save-git-config`

**功能**: 保存自定义 Git 路径

**请求体**:
```json
{
  "git_path": "C:\\Program Files\\Git\\bin\\git.exe"
}
```

**响应**:
```json
{
  "success": true,
  "message": "Git 配置已保存"
}
```

---

## 🧪 5. 测试模型连接

### POST `/api/initialization/test-model`

**功能**: 测试 API Key 是否有效

**请求体**:
```json
{
  "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
}
```

**响应** (成功):
```json
{
  "success": true,
  "message": "连接成功",
  "response": "Hello! I'm working properly."
}
```

**响应** (失败):
```json
{
  "success": false,
  "error": "API Key 无效或已过期"
}
```

---

## 🔍 6. 检测 Git

### POST `/api/initialization/detect-git`

**功能**: 自动检测系统 Git

**响应**:
```json
{
  "success": true,
  "git_detected": true,
  "git_version": "2.43.0",
  "git_path": "C:\\Program Files\\Git\\bin\\git.exe"
}
```

---

## ✅ 7. 完成初始化

### POST `/api/initialization/complete`

**功能**: 标记初始化完成

**响应**:
```json
{
  "success": true,
  "message": "初始化已完成"
}
```

**实现**:
```python
@router.post("/complete")
async def complete_initialization():
    storage = BackendStorage()
    
    from datetime import datetime
    storage.set("webui_initialized", True)
    storage.set("webui_initialized_at", datetime.now().isoformat())
    
    logger.info("初始化已完成")
    
    return {
        "success": True,
        "message": "初始化已完成"
    }
```

---

## 🛡️ 错误处理

### 统一错误响应格式

```json
{
  "success": false,
  "error": "错误信息",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

### 常见错误码

| 错误码 | 说明 |
|--------|------|
| `VALIDATION_ERROR` | 参数验证失败 |
| `CONFIG_LOAD_ERROR` | 配置文件加载失败 |
| `CONFIG_SAVE_ERROR` | 配置文件保存失败 |
| `API_TEST_FAILED` | API 测试失败 |
| `GIT_NOT_FOUND` | 未检测到 Git |
| `PERMISSION_DENIED` | 权限不足 |

---

## 🔐 认证机制

所有初始化 API 都需要通过 WebUI 认证：

```python
from src.common.security import VerifiedDep

@router.post("/save-bot-config")
async def save_bot_config(request: BotConfigRequest, _=VerifiedDep):
    # 处理逻辑
    pass
```

---

**返回**: [README](./README.md) | **上一篇**: [流程设计](./flow-design.md)
