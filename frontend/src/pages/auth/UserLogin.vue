<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { BookOpen, User, Lock, ArrowRight, Loader2 } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const formData = new FormData()
    formData.append('username', username.value)
    formData.append('password', password.value)
    
    // Login
    const res = await axios.post('/api/auth/login', formData)
    const token = res.data.access_token
    
    // Set token
    authStore.setToken(token)
    
    // Fetch user details
    await authStore.fetchUser()
    
    // Redirect
    router.push('/')
  } catch (err: any) {
    console.error(err)
    if (err.response?.status === 401) {
      error.value = '用户名或密码错误'
    } else {
      error.value = '登录失败，请重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex bg-white">
    <!-- Left Side - Image -->
    <div class="hidden lg:flex lg:w-1/2 relative bg-gray-900">
      <img 
        src="https://images.unsplash.com/photo-1507842217343-583bb7270b66?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80" 
        alt="Library" 
        class="absolute inset-0 w-full h-full object-cover opacity-60"
      />
      <div class="relative z-10 w-full flex flex-col justify-center px-12 text-white">
        <div class="flex items-center gap-3 mb-8">
          <BookOpen class="w-10 h-10 text-blue-400" />
          <h1 class="text-4xl font-bold tracking-tight">智图悦读</h1>
        </div>
        <h2 class="text-3xl font-bold mb-6">用 AI 发现您的下一本爱书</h2>
        <p class="text-lg text-gray-300 max-w-md">
          我们的智能推荐系统会分析您的阅读历史和偏好，为您推荐您绝对会喜欢的书籍。
        </p>
      </div>
    </div>

    <!-- Right Side - Form -->
    <div class="flex-1 flex items-center justify-center p-4 sm:p-12 lg:p-24 bg-white">
      <div class="w-full max-w-sm space-y-10">
        <div class="text-center lg:text-left">
          <h2 class="text-3xl font-bold tracking-tight text-gray-900">欢迎回来</h2>
          <p class="mt-2 text-sm text-gray-600">
            请输入您的详细信息以登录
          </p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <div class="space-y-5">
            <div>
              <label for="username" class="block text-sm font-medium leading-6 text-gray-900">用户名</label>
              <div class="relative mt-2 rounded-md shadow-sm">
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <User class="h-5 w-5 text-gray-400" aria-hidden="true" />
                </div>
                <input
                  id="username"
                  v-model="username"
                  name="username"
                  type="text"
                  required
                  class="block w-full rounded-md border-0 py-2.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 transition-all"
                  placeholder="请输入用户名"
                />
              </div>
            </div>

            <div>
              <div class="flex items-center justify-between">
                <label for="password" class="block text-sm font-medium leading-6 text-gray-900">密码</label>
                <div class="text-sm">
                  <a href="#" class="font-semibold text-blue-600 hover:text-blue-500">忘记密码？</a>
                </div>
              </div>
              <div class="relative mt-2 rounded-md shadow-sm">
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Lock class="h-5 w-5 text-gray-400" aria-hidden="true" />
                </div>
                <input
                  id="password"
                  v-model="password"
                  name="password"
                  type="password"
                  required
                  class="block w-full rounded-md border-0 py-2.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 transition-all"
                  placeholder="••••••••"
                />
              </div>
            </div>
          </div>

          <div v-if="error" class="p-3 rounded-md bg-red-50 text-red-600 text-sm flex items-center gap-2 animate-pulse">
            <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>
            {{ error }}
          </div>

          <button 
            type="submit" 
            :disabled="loading"
            class="flex w-full justify-center items-center gap-2 rounded-md bg-blue-600 px-3 py-2.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
          >
            <Loader2 v-if="loading" class="w-5 h-5 animate-spin" />
            <span v-else>登录</span>
            <ArrowRight v-if="!loading" class="w-4 h-4" />
          </button>
          
          <div class="relative">
            <div class="absolute inset-0 flex items-center" aria-hidden="true">
              <div class="w-full border-t border-gray-200"></div>
            </div>
            <div class="relative flex justify-center">
              <span class="bg-white px-2 text-sm text-gray-500">还没有账号？</span>
            </div>
          </div>
          
          <div class="mt-6 grid grid-cols-1">
             <RouterLink to="/register" class="flex w-full items-center justify-center gap-3 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus-visible:ring-transparent transition-all">
               免费注册
             </RouterLink>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
