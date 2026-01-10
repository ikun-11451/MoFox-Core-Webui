# 实时日志 JSON 解析错误修复方案

## 问题描述

在实时日志查看页面（LiveLogView.vue）中，频繁出现以下错误：

```
日志消息不是有效的 JSON 格式: SyntaxError: Expected ',' or '}' after property value in JSON at position 45
```

**错误示例日志：**
```javascript
原始日志消息: {'logger_name': 'model_utils', 'event': "任务-'semantic_annotation' 模型-'gemini-2.5-pro': 连接异常，将于2秒后重试 (5次剩余)。", 'level': 'warning', 'timestamp': '01-10 10:27:09', 'color': '#D700D7'}
```

## 根本原因分析

### 数据流追踪

1. **后端日志生成**（`mmc/src/common/log_broadcaster.py:154-165`）
   - `BroadcastLogHandler.emit()` 创建标准 Python 字典 `log_dict`
   - 包含字段：`timestamp`, `level`, `logger_name`, `event`, `alias`, `color`

2. **WebSocket 发送**（`MoFox-Core-Webui/backend/routers/log_viewer_router.py:508`）
   - 使用 `websocket.send_json(log_record)` 发送
   - **问题所在**：某些情况下，`log_record` 可能已经是字符串而非字典

3. **前端接收**（`LiveLogView.vue:412`）
   - `JSON.parse(event.data)` 成功解析为 JavaScript 对象
   - `logEntry.event` 字段的值是**字符串**

4. **前端显示**（`LiveLogView.vue:163`）
   - 调用 `formatLogMessage(entry.event)` 格式化消息
   - **核心问题**：`entry.event` 的值本身是 Python 字典格式的字符串！

### 问题定位

从用户提供的错误日志可以看出：

```javascript
console.log('原始日志消息:', message)
// 输出: {'logger_name': 'model_utils', 'event': "...", ...}
```

这说明传入 `formatLogMessage()` 的 `message` 参数是一个 **Python 字典格式的字符串**，而不是纯文本消息。

### 为什么会出现 Python 字典字符串？

可能的原因：
1. 后端某个环节对日志对象调用了 `str()` 或 `repr()`
2. 日志系统的某个中间层将对象序列化成了字符串
3. WebSocket 发送前进行了不正确的序列化

### 当前代码的缺陷

`LiveLogView.vue:266-270` 的转换逻辑存在严重缺陷：

```typescript
const jsonMessage = message
  .replace(/'/g, '"')  // 单引号转双引号
  .replace(/True/g, 'true')
  .replace(/False/g, 'false')
  .replace(/None/g, 'null')
```

**问题**：简单的 `replace(/'/g, '"')` 会替换**所有**单引号，包括：
- Python 字典的键值分隔符：`'logger_name': 'model_utils'` → `"logger_name": "model_utils"` ✓
- **消息内容中的单引号**：`"任务-'semantic_annotation'"` → `"任务-"semantic_annotation""` ✗

这导致 JSON 解析失败，错误信息：
```
Expected ',' or '}' after property value in JSON at position 45
```

## 修复方案

### 方案一：改进前端 Python 字典解析逻辑（推荐）

**原理**：使用更智能的解析方法，避免破坏字符串内部的引号。

**实现步骤**：

1. **使用正则表达式精确匹配 Python 字典的键**
   - 只替换作为键的单引号，不替换值中的单引号
   
2. **使用 AST 或 eval 风格的安全解析**
   - 使用 `Function` 构造器或自定义解析器

3. **添加更完善的错误处理**

**代码示例**：

```typescript
const formatLogMessage = (message: string) => {
  if (!message) return ''
  
  // 检查是否是 Python 字典格式
  if (message.trim().startsWith('{') && message.trim().endsWith('}')) {
    try {
      // 方法1：使用更安全的替换策略
      // 只替换键名周围的单引号，保留值中的单引号
      let jsonMessage = message
        // 替换键名的单引号: 'key': -> "key":
        .replace(/'([^']+)'(\s*):(\s*)/g, '"$1"$2:$3')
        // 替换布尔值和 null
        .replace(/:\s*True/g, ': true')
        .replace(/:\s*False/g, ': false')
        .replace(/:\s*None/g, ': null')
        // 处理字符串值的单引号: : 'value' -> : "value"
        // 但要小心值内部的单引号
        .replace(/:\s*'([^']*)'/g, (match, p1) => {
          // 转义值内部的双引号
          const escaped = p1.replace(/"/g, '\\"')
          return `: "${escaped}"`
        })
      
      const parsed = JSON.parse(jsonMessage)
      if (parsed && typeof parsed === 'object' && parsed.event) {
        return escapeHtml(parsed.event)
      }
    } catch (e) {
      console.warn('解析 Python 字典格式失败，尝试直接使用:', e)
    }
  }
  
  // 如果不是字典格式或解析失败，作为普通文本处理
  // ... 处理 ANSI 转义序列的代码 ...
}
```

**优点**：
- 不修改后端代码
- 兼容当前数据格式
- 提供更好的容错性

**缺点**：
- 复杂的字符串处理可能仍有边界情况
- 性能略低于直接处理

### 方案二：修复后端数据格式（治本）

**原理**：确保后端发送的 `event` 字段是纯文本消息，而不是序列化的对象。

**需要检查的位置**：
1. 日志生成时是否正确提取了消息文本
2. WebSocket 发送前是否有额外的序列化步骤
3. 日志广播器是否正确处理了日志记录

**实施难度**：需要深入调试后端日志系统

### 方案三：简化前端逻辑（临时方案）

如果 `entry.event` 确实是 Python 字典字符串，最简单的方案是：

```typescript
const formatLogMessage = (message: string) => {
  if (!message) return ''
  
  // 如果是 Python 字典格式，尝试提取 event 字段
  if (message.includes("'event':") || message.includes('"event":')) {
    // 使用简单的正则提取 event 值
    const eventMatch = message.match(/'event':\s*["']([^"']+)["']/) ||
                      message.match(/"event":\s*["']([^"']+)["']/)
    if (eventMatch && eventMatch[1]) {
      return escapeHtml(eventMatch[1])
    }
  }
  
  // 否则直接返回原始消息
  return escapeHtml(message)
}
```

## 推荐实施方案

**阶段1：紧急修复（使用方案三）**
- 快速解决当前错误
- 确保用户界面正常工作

**阶段2：完善修复（使用方案一）**
- 实现更健壮的 Python 字典解析
- 处理更多边界情况

**阶段3：根本解决（调查方案二）**
- 调查为什么 `event` 字段包含完整的 Python 字典
- 修复后端数据格式问题

## 测试用例

修复后需要验证以下场景：

1. **普通文本消息**
   ```
   "连接数据库成功"
   ```

2. **包含单引号的消息**
   ```
   "任务-'semantic_annotation' 模型-'gemini-2.5-pro': 连接异常"
   ```

3. **包含双引号的消息**
   ```
   "Error: "connection refused" from server"
   ```

4. **Python 字典格式**
   ```
   {'logger_name': 'test', 'event': "消息内容", 'level': 'info'}
   ```

5. **ANSI 颜色代码**
   ```
   "\x1b[31m错误消息\x1b[0m"
   ```

## 相关文件

- `MoFox-Core-Webui/forward/mofox-webui/src/views/LiveLogView.vue` (第252-373行)
- `MoFox-Core-Webui/backend/routers/log_viewer_router.py` (第496-540行)
- `mmc/src/common/log_broadcaster.py` (第107-242行)

## 修复时间估算

- 方案一（前端改进）：2-3小时
- 方案二（后端调查）：4-6小时
- 方案三（临时方案）：30分钟

## 风险评估

- **低风险**：方案三（简单正则提取）
- **中风险**：方案一（复杂字符串处理可能有遗漏）
- **高风险**：方案二（可能影响整个日志系统）

## 总结

当前问题的核心是 `entry.event` 字段包含了 Python 字典格式的字符串，而不是纯文本消息。简单的单引号替换策略会破坏消息内容中的引号，导致 JSON 解析失败。

建议先使用**方案三**快速修复，然后逐步实施**方案一**和**方案二**，最终彻底解决数据格式问题。