# Git 路由重构方案

## ✅ 已完成

重构已于 2026年1月2日 完成。

---

## 📊 变更摘要

### 后端变更

| 文件 | 变更 |
|------|------|
| `git_update_router.py` | 删除了 `/install`, `/set-path`, `/clear-path` 路由；`GitStatusResponse` 改为 `RepoStatusResponse` |
| `git_env_router.py` | 新增 `/auto-detect` 接口；移除仓库相关字段 |
| `utils/update/models.py` | `GitStatusResponse` 移除 `is_git_repo`, `current_branch`, `available_branches` 字段 |

### 前端变更

| 文件 | 变更 |
|------|------|
| `git_update.ts` | `GitStatus` 改为 `RepoStatus`；`getGitStatus()` 改为 `getRepoStatus()` |
| `git_env.ts` | 新增 `autoDetectGit()` 函数；移除 `GitEnvStatus` 中的仓库字段 |
| `GitSettingsTab.vue` | 添加"自动寻找"按钮和"下载便携版 Git"按钮 |
| `MainUpdateTab.vue` | 使用 `gitEnvStatus` + `repoStatus` 替代原来的 `gitStatus` |

---

## 🎯 重构后职责划分

| 路由组件 | 路径前缀 | 职责 |
|----------|----------|------|
| `git_env_router` | `/git_env` | Git 环境检测、安装、路径配置、自动检测 |
| `git_update_router` | `/git_update` | 主程序更新、回滚、分支管理、历史版本 |

### git_env_router 路由列表

| 路由 | 方法 | 功能 |
|------|------|------|
| `/status` | GET | 获取 Git 环境状态 |
| `/install` | POST | 下载安装便携版 Git |
| `/set-path` | POST | 设置自定义 Git 路径 |
| `/clear-path` | DELETE | 清除自定义路径 |
| `/install-guide` | GET | 获取安装指南 |
| `/auto-detect` | POST | 自动检测系统中的 Git |

### git_update_router 路由列表

| 路由 | 方法 | 功能 |
|------|------|------|
| `/status` | GET | 获取主程序仓库状态 |
| `/check` | GET | 检查主程序更新 |
| `/update` | POST | 更新主程序 |
| `/rollback` | POST | 回滚版本 |
| `/switch-branch` | POST | 切换分支 |
| `/backups` | GET | 获取历史版本 |
| `/commits/{hash}` | GET | 获取提交详情 |

---

## 🆕 新增功能

### 自动寻找 Git 按钮
- 位置：Git 设置页面 → Git 路径卡片
- 功能：清除当前配置，重新自动检测系统/便携版 Git

### 下载便携版按钮
- 位置：Git 设置页面 → Git 路径卡片（仅在未检测到 Git 且为 Windows 时显示）
- 功能：下载并安装 Windows 便携版 Git

---

*完成时间：2026年1月2日*
