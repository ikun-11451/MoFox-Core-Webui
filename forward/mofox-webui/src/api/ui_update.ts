/**
 * UI 更新 API
 * 管理 WebUI 静态文件的更新检查、下载和回滚
 */
import { api } from './index'

// ==================== 类型定义 ====================

/**
 * UI 状态响应（合并了版本信息和更新检查）
 */
export interface UIStatusResult {
  success: boolean
  // 是否有更新
  has_update: boolean
  // 当前版本
  current_version?: string
  current_commit?: string
  // 远程版本
  latest_version?: string
  latest_commit?: string
  // 更新日志
  changelog: string[]
  commits_behind?: number
  // 更新功能是否启用
  update_enabled?: boolean
  // 当前分支
  current_branch?: string
  // 提示信息
  message?: string
  // 错误信息
  error?: string
}

export interface UIUpdateResult {
  success: boolean
  message: string
  version?: string
  backup_name?: string
  error?: string
}

export interface UIBackupInfo {
  name: string
  version?: string
  timestamp: string
  size?: number
}

// ==================== API 函数 ====================

/**
 * 获取 UI 状态（包含版本信息和更新检查）
 */
export function getUIStatus() {
  return api.get<UIStatusResult>('ui_update/status')
}

/**
 * 执行 UI 更新
 */
export function updateUI() {
  return api.post<UIUpdateResult>('ui_update/update')
}

/**
 * 获取 UI 备份列表
 */
export function getUIBackups() {
  return api.get<{ success: boolean; data: UIBackupInfo[]; error?: string }>('ui_update/backups')
}

/**
 * 回滚 UI 版本
 */
export function rollbackUI(backupName: string) {
  return api.post<UIUpdateResult>('ui_update/rollback', {
    backup_name: backupName
  })
}
