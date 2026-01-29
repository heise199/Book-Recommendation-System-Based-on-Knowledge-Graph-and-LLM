import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(sessionStorage.getItem('token'))
  const user = ref<any | null>(JSON.parse(sessionStorage.getItem('user') || 'null'))
  const isAdmin = computed(() => user.value?.is_superuser || false)

  const API_URL = 'http://localhost:8000'
  axios.defaults.baseURL = API_URL

  if (token.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }

  const router = useRouter()

  function setToken(newToken: string) {
    token.value = newToken
    sessionStorage.setItem('token', newToken)
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
  }

  function setUser(newUser: any) {
    user.value = newUser
    sessionStorage.setItem('user', JSON.stringify(newUser))
  }

  function logout() {
    token.value = null
    user.value = null
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await axios.get('/api/users/me')
      setUser(response.data)
    } catch (error) {
      console.error('Failed to fetch user', error)
      logout()
    }
  }

  return {
    token,
    user,
    isAdmin,
    setToken,
    setUser,
    logout,
    fetchUser
  }
})
