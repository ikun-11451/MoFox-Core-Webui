import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('mofox_token'))

  function login(apiKey: string) {
    token.value = apiKey
    localStorage.setItem('mofox_token', apiKey)
    return true
  }

  function logout() {
    token.value = null
    localStorage.removeItem('mofox_token')
  }

  function isAuthenticated() {
    return !!token.value
  }

  function getToken() {
    return token.value
  }

  return {
    token,
    login,
    logout,
    isAuthenticated,
    getToken
  }
})
