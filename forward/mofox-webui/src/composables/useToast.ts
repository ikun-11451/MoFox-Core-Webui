import { createApp, type App } from 'vue'
import ToastComponent from '@/components/common/Toast.vue'

let toastInstance: any = null

export function setupToast() {
  if (!toastInstance) {
    const container = document.createElement('div')
    document.body.appendChild(container)
    
    const app = createApp(ToastComponent)
    const instance = app.mount(container)
    
    toastInstance = instance
  }
  
  return toastInstance
}

export interface ToastOptions {
  type?: 'success' | 'error' | 'warning' | 'info'
  message: string
  title?: string
  duration?: number
}

export function useToast() {
  const toast = toastInstance || setupToast()
  
  return {
    show(options: ToastOptions) {
      return toast.addToast({
        type: options.type || 'info',
        ...options
      })
    },
    
    success(message: string, title?: string, duration?: number) {
      return toast.addToast({
        type: 'success',
        message,
        title,
        duration
      })
    },
    
    error(message: string, title?: string, duration?: number) {
      return toast.addToast({
        type: 'error',
        message,
        title,
        duration
      })
    },
    
    warning(message: string, title?: string, duration?: number) {
      return toast.addToast({
        type: 'warning',
        message,
        title,
        duration
      })
    },
    
    info(message: string, title?: string, duration?: number) {
      return toast.addToast({
        type: 'info',
        message,
        title,
        duration
      })
    },
    
    remove(id: number) {
      return toast.removeToast(id)
    }
  }
}

// 全局安装插件
export function installToast(app: App) {
  const toast = setupToast()
  
  app.config.globalProperties.$toast = {
    show: (options: ToastOptions) => toast.addToast(options),
    success: (message: string, title?: string, duration?: number) => 
      toast.addToast({ type: 'success', message, title, duration }),
    error: (message: string, title?: string, duration?: number) => 
      toast.addToast({ type: 'error', message, title, duration }),
    warning: (message: string, title?: string, duration?: number) => 
      toast.addToast({ type: 'warning', message, title, duration }),
    info: (message: string, title?: string, duration?: number) => 
      toast.addToast({ type: 'info', message, title, duration })
  }
}
