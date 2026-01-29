<script setup lang="ts">
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { LayoutDashboard, Users, Book, LogOut, Menu, X, Bell, Search, Settings } from 'lucide-vue-next'
import { ref } from 'vue'

const authStore = useAuthStore()
const router = useRouter()
const isSidebarOpen = ref(false)

const handleLogout = () => {
  authStore.logout()
  router.push('/admin/login')
}

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex">
    <!-- Sidebar Backdrop for Mobile -->
    <div 
      v-if="isSidebarOpen" 
      class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 lg:hidden"
      @click="toggleSidebar"
    ></div>

    <!-- Sidebar -->
    <aside 
      class="fixed lg:static inset-y-0 left-0 z-50 w-64 bg-slate-900 text-white transform transition-transform duration-300 ease-in-out lg:transform-none flex flex-col shadow-2xl lg:shadow-none"
      :class="isSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="h-16 flex items-center px-6 border-b border-slate-800">
        <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                <span class="font-bold text-lg">A</span>
            </div>
            <h1 class="text-lg font-bold tracking-wide">
            智图<span class="text-blue-400">管理</span>
            </h1>
        </div>
        <button class="ml-auto lg:hidden text-slate-400 hover:text-white" @click="toggleSidebar">
            <X class="w-5 h-5" />
        </button>
      </div>
      
      <div class="flex-1 overflow-y-auto py-6 px-3 space-y-1">
        <div class="px-3 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
            概览
        </div>
        <RouterLink to="/admin/dashboard" active-class="bg-blue-600 text-white shadow-lg shadow-blue-600/20" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition-all group">
          <LayoutDashboard class="w-5 h-5 group-hover:scale-110 transition-transform" />
          <span class="font-medium">仪表盘</span>
        </RouterLink>
        
        <div class="px-3 mt-6 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
            管理
        </div>
        <RouterLink to="/admin/users" active-class="bg-blue-600 text-white shadow-lg shadow-blue-600/20" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition-all group">
          <Users class="w-5 h-5 group-hover:scale-110 transition-transform" />
          <span class="font-medium">用户管理</span>
        </RouterLink>
        <RouterLink to="/admin/books" active-class="bg-blue-600 text-white shadow-lg shadow-blue-600/20" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition-all group">
          <Book class="w-5 h-5 group-hover:scale-110 transition-transform" />
          <span class="font-medium">图书管理</span>
        </RouterLink>

        <div class="px-3 mt-6 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
            系统
        </div>
        <a href="#" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition-all group">
            <Settings class="w-5 h-5 group-hover:scale-110 transition-transform" />
            <span class="font-medium">系统设置</span>
        </a>
      </div>

      <div class="p-4 border-t border-slate-800">
        <div class="flex items-center gap-3 px-3 py-3 rounded-xl bg-slate-800/50 border border-slate-700/50">
          <div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold">
            {{ authStore.user?.username?.charAt(0).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-white truncate">{{ authStore.user?.username }}</p>
            <p class="text-xs text-slate-400 truncate">管理员</p>
          </div>
          <button @click="handleLogout" class="text-slate-400 hover:text-red-400 transition-colors p-1" title="退出登录">
            <LogOut class="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Header -->
      <header class="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-4 lg:px-8 z-10 sticky top-0">
        <div class="flex items-center gap-4">
            <button @click="toggleSidebar" class="lg:hidden p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
                <Menu class="w-5 h-5" />
            </button>
            <div class="relative hidden sm:block max-w-md w-full">
                <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input 
                    type="text" 
                    placeholder="搜索..." 
                    class="pl-10 pr-4 py-2 bg-gray-50 border-none rounded-lg text-sm focus:ring-2 focus:ring-blue-500 w-64 transition-all focus:w-80"
                />
            </div>
        </div>

        <div class="flex items-center gap-4">
            <button class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full relative transition-colors">
                <Bell class="w-5 h-5" />
                <span class="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
            </button>
            <div class="h-8 w-px bg-gray-200 hidden sm:block"></div>
            <div class="flex items-center gap-2">
                 <span class="text-sm font-medium text-gray-700 hidden sm:block">管理控制台</span>
            </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 lg:p-8 scroll-smooth">
        <slot />
      </main>
    </div>
  </div>
</template>
