<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { BookOpen, User, Lock, Mail, ArrowRight, Loader2 } from 'lucide-vue-next'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const gender = ref('')
const age = ref<number | ''>('')
const selectedCategories = ref<string[]>([])
const error = ref('')
const loading = ref(false)

const categories = ["科幻", "历史", "计算机", "经济管理", "心理学", "悬疑"]

const toggleCategory = (cat: string) => {
  if (selectedCategories.value.includes(cat)) {
    selectedCategories.value = selectedCategories.value.filter(c => c !== cat)
  } else {
    selectedCategories.value.push(cat)
  }
}

const handleRegister = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    const payload = {
      username: username.value,
      email: email.value || undefined,
      password: password.value,
      gender: gender.value || undefined,
      age: age.value || undefined,
      preferred_categories: selectedCategories.value.join(',') || undefined
    }
    
    // Register
    await axios.post('/api/auth/register', payload)
    
    // Redirect to login
    router.push('/login')
  } catch (err: any) {
    console.error(err)
    if (err.response?.status === 400) {
      error.value = err.response.data.detail || '注册失败'
    } else {
      error.value = '注册失败，请重试'
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
        src="https://images.unsplash.com/photo-1481627834876-b7833e8f5570?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80" 
        alt="Library" 
        class="absolute inset-0 w-full h-full object-cover opacity-60"
      />
      <div class="relative z-10 w-full flex flex-col justify-center px-12 text-white">
        <div class="flex items-center gap-3 mb-8">
          <BookOpen class="w-10 h-10 text-blue-400" />
          <h1 class="text-4xl font-bold tracking-tight">智图悦读</h1>
        </div>
        <h2 class="text-3xl font-bold mb-6">加入我们的阅读社区</h2>
        <p class="text-lg text-gray-300 max-w-md">
          创建账号，开始您的个性化阅读之旅。探索、收藏、分享您喜爱的书籍。
        </p>
      </div>
    </div>

    <!-- Right Side - Form -->
    <div class="flex-1 flex items-center justify-center p-4 sm:p-12 lg:p-24 bg-white">
      <div class="w-full max-w-sm space-y-10">
        <div class="text-center lg:text-left">
          <h2 class="text-3xl font-bold tracking-tight text-gray-900">创建新账号</h2>
          <p class="mt-2 text-sm text-gray-600">
            已有账号？
            <RouterLink to="/login" class="font-semibold text-blue-600 hover:text-blue-500">立即登录</RouterLink>
          </p>
        </div>

        <form @submit.prevent="handleRegister" class="space-y-6">
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
                  class="block w-full rounded-md border-0 py-1.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 transition-all" 
                  placeholder="请输入用户名" 
                />
              </div>
            </div>

            <div>
              <label for="email" class="block text-sm font-medium leading-6 text-gray-900">邮箱 (可选)</label>
              <div class="relative mt-2 rounded-md shadow-sm">
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Mail class="h-5 w-5 text-gray-400" aria-hidden="true" />
                </div>
                <input 
                  id="email" 
                  v-model="email"
                  name="email" 
                  type="email" 
                  class="block w-full rounded-md border-0 py-1.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 transition-all" 
                  placeholder="name@example.com" 
                />
              </div>
            </div>

            <div>
              <label for="password" class="block text-sm font-medium leading-6 text-gray-900">密码</label>
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
                  class="block w-full rounded-md border-0 py-1.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 transition-all" 
                  placeholder="••••••••" 
                />
              </div>
            </div>

            <div>
              <label for="confirmPassword" class="block text-sm font-medium leading-6 text-gray-900">确认密码</label>
              <div class="relative mt-2 rounded-md shadow-sm">
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Lock class="h-5 w-5 text-gray-400" aria-hidden="true" />
                </div>
                <input 
                  id="confirmPassword" 
                  v-model="confirmPassword"
                  name="confirmPassword" 
                  type="password" 
                  required 
                  class="block w-full rounded-md border-0 py-1.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 transition-all" 
                  placeholder="••••••••" 
                />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="gender" class="block text-sm font-medium leading-6 text-gray-900">性别</label>
                <select id="gender" v-model="gender" class="mt-2 block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-blue-600 sm:text-sm sm:leading-6">
                  <option value="">请选择</option>
                  <option value="male">男</option>
                  <option value="female">女</option>
                  <option value="other">其他</option>
                </select>
              </div>
              <div>
                <label for="age" class="block text-sm font-medium leading-6 text-gray-900">年龄</label>
                <input type="number" id="age" v-model="age" min="1" max="120" class="mt-2 block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6" placeholder="可选" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium leading-6 text-gray-900 mb-2">感兴趣的分类</label>
              <div class="flex flex-wrap gap-2">
                <button 
                  v-for="cat in categories" 
                  :key="cat"
                  type="button"
                  @click="toggleCategory(cat)"
                  :class="[
                    'px-3 py-1.5 text-xs font-medium rounded-full border transition-all',
                    selectedCategories.includes(cat) 
                      ? 'bg-blue-600 text-white border-blue-600 shadow-sm' 
                      : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300 hover:text-blue-600'
                  ]"
                >
                  {{ cat }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="error" class="p-3 rounded-lg bg-red-50 text-red-600 text-sm flex items-center gap-2">
             <div class="w-1.5 h-1.5 rounded-full bg-red-600"></div>
             {{ error }}
          </div>

          <button 
            type="submit" 
            :disabled="loading"
            class="group relative flex w-full justify-center items-center gap-2 rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
            <span v-else>注册账号</span>
            <ArrowRight v-if="!loading" class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
