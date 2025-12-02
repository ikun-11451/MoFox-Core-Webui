import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('mofox_token'))

  function login() {
    // 模拟登录逻辑
    const newToken = 'demo_token_' + Date.now()
    token.value = newToken
    localStorage.setItem('mofox_token', newToken)
    return true
  }

  function logout() {
    token.value = null
    localStorage.removeItem('mofox_token')
  }

  function isAuthenticated() {
    return !!token.value
  }

  return {
    token,
    login,
    logout,
    isAuthenticated
  }
})
