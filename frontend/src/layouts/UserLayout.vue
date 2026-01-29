<script setup lang="ts">
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { BookOpen, User, LogOut, LogIn, Github, Twitter, Linkedin } from 'lucide-vue-next'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 font-sans text-gray-900 flex flex-col">
    <header class="fixed top-0 left-0 right-0 z-50 transition-all duration-300 bg-white/80 backdrop-blur-md border-b border-gray-200/50 supports-[backdrop-filter]:bg-white/60">
      <div class="container mx-auto px-4 h-16 flex items-center justify-between">
        <RouterLink to="/" class="flex items-center gap-2 group">
          <div class="p-1.5 bg-blue-600 rounded-lg text-white group-hover:bg-blue-700 transition-colors">
            <BookOpen class="w-5 h-5" />
          </div>
          <span class="text-xl font-bold tracking-tight text-gray-900">智图悦读</span>
        </RouterLink>

        <nav class="hidden md:flex items-center gap-8">
          <RouterLink to="/" class="text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors">首页</RouterLink>
          <div class="relative group" v-if="authStore.token">
             <RouterLink to="/profile" class="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors">
               <span>我的书房</span>
             </RouterLink>
          </div>
          <a href="#" class="text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors">关于我们</a>
        </nav>

        <div class="flex items-center gap-4">
          <template v-if="authStore.token">
            <div class="flex items-center gap-3 pl-4 border-l border-gray-200">
              <div class="text-right hidden sm:block">
                <p class="text-xs text-gray-500">欢迎回来</p>
                <p class="text-sm font-semibold text-gray-900 leading-none">{{ authStore.user?.username }}</p>
              </div>
              <button @click="handleLogout" class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-all" title="退出登录">
                <LogOut class="w-5 h-5" />
              </button>
            </div>
          </template>
          <template v-else>
            <RouterLink to="/login" class="flex items-center gap-2 px-4 py-2 rounded-full bg-gray-900 text-white text-sm font-medium hover:bg-gray-800 transition-all shadow-lg shadow-gray-900/20">
              <LogIn class="w-4 h-4" />
              <span>登录</span>
            </RouterLink>
          </template>
        </div>
      </div>
    </header>

    <main class="flex-1 container mx-auto px-4 pt-24 pb-12">
      <slot />
    </main>

    <footer class="bg-white border-t border-gray-200 py-12 mt-auto">
      <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center gap-6">
          <div class="flex items-center gap-2">
            <div class="p-1 bg-gray-900 rounded text-white">
              <BookOpen class="w-4 h-4" />
            </div>
            <span class="text-lg font-bold text-gray-900">智图悦读</span>
          </div>
          
          <div class="flex gap-6 text-sm text-gray-500">
            <a href="#" class="hover:text-gray-900 transition-colors">隐私政策</a>
            <a href="#" class="hover:text-gray-900 transition-colors">服务条款</a>
            <a href="#" class="hover:text-gray-900 transition-colors">联系我们</a>
          </div>

          <div class="flex gap-4">
            <a href="#" class="text-gray-400 hover:text-gray-900 transition-colors">
              <Github class="w-5 h-5" />
            </a>
            <a href="#" class="text-gray-400 hover:text-blue-400 transition-colors">
              <Twitter class="w-5 h-5" />
            </a>
            <a href="#" class="text-gray-400 hover:text-blue-700 transition-colors">
              <Linkedin class="w-5 h-5" />
            </a>
          </div>
        </div>
        <div class="mt-8 pt-8 border-t border-gray-100 text-center text-sm text-gray-400">
          &copy; {{ new Date().getFullYear() }} 智图悦读. 版权所有.
        </div>
      </div>
    </footer>
  </div>
</template>
