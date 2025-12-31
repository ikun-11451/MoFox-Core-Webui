import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'
import DashboardHome from '@/views/DashboardHome.vue'
import BotConfigView from '@/views/BotConfigView.vue'
import ModelConfigView from '@/views/ModelConfigView.vue'
import PluginConfigList from '@/views/PluginConfigList.vue'
import PluginConfigView from '@/views/PluginConfigView.vue'
import PluginManageView from '@/views/PluginManageView.vue'
import PluginDetailView from '@/views/PluginDetailView.vue'
import PluginMarketplace from '@/views/PluginMarketplace.vue'
import PluginMarketplaceDetail from '@/views/PluginMarketplaceDetail.vue'
import GitUpdateView from '@/views/GitUpdateView.vue'
import LogViewerView from '@/views/LogViewerView.vue'
import LiveLogView from '@/views/LiveLogView.vue'
import ExpressionView from '@/views/ExpressionView.vue'
import RelationshipView from '@/views/RelationshipView.vue'
import ThemeConfigView from '@/views/ThemeConfigView.vue'
import ChatroomView from '@/views/ChatroomView.vue'
import LiveChatView from '@/views/LiveChatView.vue'
import GitHubView from '@/views/GitHubView.vue'
import EmojiManager from '@/components/emoji/EmojiManager.vue'
import ModelStatsView from '@/views/ModelStatsView.vue'
import InitializationView from '@/views/InitializationView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/initialization',
    name: 'Initialization',
    component: InitializationView,
    meta: { requiresAuth: true, skipInitCheck: true }
  },
  {
    path: '/dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'DashboardHome',
        component: DashboardHome
      },
      {
        path: 'model-stats',
        name: 'ModelStats',
        component: ModelStatsView
      },
      {
        path: 'theme',
        name: 'ThemeConfig',
        component: ThemeConfigView
      },
      {
        path: 'bot-config',
        name: 'BotConfig',
        component: BotConfigView
      },
      {
        path: 'model-config',
        name: 'ModelConfig',
        component: ModelConfigView
      },
      {
        path: 'plugin-config',
        name: 'PluginConfigList',
        component: PluginConfigList
      },
      {
        path: 'plugin-config/:path(.*)',
        name: 'PluginConfigView',
        component: PluginConfigView,
        props: true
      },
      {
        path: 'plugin-manage',
        name: 'PluginManage',
        component: PluginManageView
      },
      {
        path: 'plugin-manage/:pluginName',
        name: 'PluginDetail',
        component: PluginDetailView,
        props: true
      },
      {
        path: 'marketplace',
        name: 'PluginMarketplace',
        component: PluginMarketplace
      },
      {
        path: 'marketplace/:pluginId',
        name: 'PluginMarketplaceDetail',
        component: PluginMarketplaceDetail,
        props: true
      },
      {
        path: 'expression',
        name: 'Expression',
        component: ExpressionView
      },
      {
        path: 'relationship',
        name: 'Relationship',
        component: RelationshipView
      },
      {
        path: 'emoji-manager',
        name: 'EmojiManager',
        component: EmojiManager
      },
      {
        path: 'chatroom',
        name: 'Chatroom',
        component: ChatroomView
      },
      {
        path: 'live-chat',
        name: 'LiveChat',
        component: LiveChatView
      },
      {
        path: 'git-update',
        name: 'GitUpdate',
        component: GitUpdateView
      },
      {
        path: 'github',
        name: 'GitHub',
        component: GitHubView
      },
      {
        path: 'log-viewer',
        name: 'LogViewer',
        component: LogViewerView
      },
      {
        path: 'live-log',
        name: 'LiveLog',
        component: LiveLogView
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导入初始化状态检查API
import { getInitStatus } from '@/api/initialization'

// 缓存初始化状态，避免重复请求
let initStatusCache: { isInitialized: boolean; timestamp: number } | null = null
const CACHE_DURATION = 60000 // 缓存1分钟

// 获取初始化状态（带缓存）
async function checkInitStatus(): Promise<boolean> {
  const now = Date.now()
  
  // 如果有有效缓存，直接返回
  if (initStatusCache && (now - initStatusCache.timestamp) < CACHE_DURATION) {
    return initStatusCache.isInitialized
  }
  
  try {
    const result = await getInitStatus()
    if (result.success && result.data) {
      // 更新缓存
      initStatusCache = {
        isInitialized: result.data.is_initialized,
        timestamp: now
      }
      return result.data.is_initialized
    }
  } catch (error) {
    console.error('检查初始化状态失败:', error)
  }
  
  // 出错时返回 true，允许继续访问（避免阻塞）
  return true
}

// 清除初始化状态缓存（用于初始化完成后）
export function clearInitStatusCache() {
  initStatusCache = null
}

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  const isAuthenticated = localStorage.getItem('mofox_token')
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }
  
  // 登录页逻辑
  if (to.path === '/login' && isAuthenticated) {
    next('/dashboard')
    return
  }
  
  // 检查初始化状态（仅在已认证且不跳过初始化检查的页面）
  if (isAuthenticated && !to.meta.skipInitCheck) {
    const isInitialized = await checkInitStatus()
    
    if (!isInitialized) {
      // 未初始化，重定向到初始化页面
      if (to.path !== '/initialization') {
        next('/initialization')
        return
      }
    } else {
      // 已初始化，不允许访问初始化页面
      if (to.path === '/initialization') {
        next('/dashboard')
        return
      }
    }
  }
  
  next()
})

export default router
