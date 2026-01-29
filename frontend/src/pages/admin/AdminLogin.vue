<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { Lock, ShieldCheck, ArrowRight, Loader2 } from 'lucide-vue-next'

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
    
    // Set token temporarily to fetch user
    authStore.setToken(token)
    
    // Fetch user details
    await authStore.fetchUser()
    
    // Check if admin
    if (!authStore.isAdmin) {
      error.value = '访问拒绝。需要管理员权限。'
      authStore.logout()
    } else {
      // Redirect to dashboard
      router.push('/admin/dashboard')
    }
  } catch (err: any) {
    console.error(err)
    if (err.response?.status === 401) {
      error.value = '凭证无效'
    } else {
      error.value = '登录失败，请重试。'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-900 relative overflow-hidden">
    <!-- Background Effects -->
    <div class="absolute inset-0 overflow-hidden">
        <div class="absolute -top-[50%] -left-[50%] w-[200%] h-[200%] bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-800 via-slate-900 to-black opacity-50"></div>
        <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent"></div>
        <div class="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent"></div>
    </div>

    <div class="w-full max-w-md relative z-10 px-6">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600/20 text-blue-400 mb-6 border border-blue-500/20 backdrop-blur-sm shadow-xl shadow-blue-900/20">
           <ShieldCheck class="w-8 h-8" />
        </div>
        <h2 class="text-3xl font-bold tracking-tight text-white mb-2">管理后台</h2>
        <p class="text-slate-400 text-sm">
          仅限授权人员访问。请登录以继续。
        </p>
      </div>
      
      <div class="bg-slate-800/50 backdrop-blur-md rounded-2xl shadow-2xl border border-slate-700/50 p-8">
        <form class="space-y-6" @submit.prevent="handleLogin">
          <div class="space-y-4">
            <div>
              <label for="username" class="block text-sm font-medium text-slate-300 mb-1.5">用户名</label>
              <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                      <Lock class="h-4 w-4" />
                  </div>
                  <input 
                    id="username" 
                    v-model="username" 
                    name="username" 
                    type="text" 
                    required 
                    class="block w-full rounded-lg border-slate-600 bg-slate-900/50 text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm pl-10 py-2.5 placeholder-slate-500 transition-colors" 
                    placeholder="admin" 
                  />
              </div>
            </div>
            
            <div>
              <label for="password" class="block text-sm font-medium text-slate-300 mb-1.5">密码</label>
              <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                      <Lock class="h-4 w-4" />
                  </div>
                  <input 
                    id="password" 
                    v-model="password" 
                    name="password" 
                    type="password" 
                    required 
                    class="block w-full rounded-lg border-slate-600 bg-slate-900/50 text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm pl-10 py-2.5 placeholder-slate-500 transition-colors" 
                    placeholder="••••••••" 
                  />
              </div>
            </div>
          </div>

          <div v-if="error" class="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2">
             <div class="w-1.5 h-1.5 rounded-full bg-red-500"></div>
             {{ error }}
          </div>

          <button 
            type="submit" 
            :disabled="loading"
            class="group relative flex w-full justify-center items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-blue-600/25"
          >
            <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
            <span v-else>进入仪表盘</span>
            <ArrowRight v-if="!loading" class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </form>
      </div>
      
      <div class="mt-8 text-center">
         <p class="text-xs text-slate-500">
            &copy; {{ new Date().getFullYear() }} 智图悦读系统. 版权所有.
         </p>
      </div>
    </div>
  </div>
</template>
