<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { Users, BookOpen, Activity, Star, TrendingUp, ArrowUpRight, ArrowDownRight, Clock } from 'lucide-vue-next'

const authStore = useAuthStore()
const stats = ref({
  users: 0,
  books: 0,
  interactions: 0,
  ratings: 0
})
const loading = ref(false)

const fetchStats = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/stats')
    stats.value = res.data
  } catch (error) {
    console.error('Failed to fetch stats', error)
  } finally {
    loading.value = false
  }
}

onMounted(fetchStats)

// Mock recent activity data
const activities = [
    { id: 1, user: 'alice', action: '评价了书籍', target: 'The Great Gatsby', time: '2分钟前', type: 'rating' },
    { id: 2, user: 'bob', action: '注册了账号', target: '', time: '15分钟前', type: 'user' },
    { id: 3, user: 'charlie', action: '收藏了', target: '1984', time: '1小时前', type: 'collection' },
    { id: 4, user: 'system', action: '数据库备份', target: '成功', time: '3小时前', type: 'system' },
]
</script>

<template>
  <AdminLayout>
    <div class="mb-8 flex justify-between items-end">
       <div>
           <h1 class="text-2xl font-bold text-gray-900">仪表盘概览</h1>
           <p class="text-gray-500 mt-1">欢迎回来，{{ authStore.user?.username }}。以下是今天的动态。</p>
       </div>
       <div class="hidden sm:flex gap-2">
           <button class="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 shadow-sm transition-all">下载报告</button>
           <button class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 shadow-lg shadow-blue-600/20 transition-all">刷新数据</button>
       </div>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
       <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
    </div>

    <div v-else class="space-y-6 animate-fade-in">
        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow relative overflow-hidden group">
                <div class="absolute right-0 top-0 w-24 h-24 bg-blue-50 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
                <div class="relative z-10">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2.5 bg-blue-100 text-blue-600 rounded-xl">
                            <Users class="w-6 h-6" />
                        </div>
                        <span class="flex items-center text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
                            +12% <ArrowUpRight class="w-3 h-3 ml-1" />
                        </span>
                    </div>
                    <p class="text-sm font-medium text-gray-500 mb-1">总用户数</p>
                    <h3 class="text-3xl font-bold text-gray-900">{{ stats.users }}</h3>
                </div>
            </div>

            <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow relative overflow-hidden group">
                <div class="absolute right-0 top-0 w-24 h-24 bg-emerald-50 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
                <div class="relative z-10">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2.5 bg-emerald-100 text-emerald-600 rounded-xl">
                            <BookOpen class="w-6 h-6" />
                        </div>
                        <span class="flex items-center text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
                            +5% <ArrowUpRight class="w-3 h-3 ml-1" />
                        </span>
                    </div>
                    <p class="text-sm font-medium text-gray-500 mb-1">总书籍数</p>
                    <h3 class="text-3xl font-bold text-gray-900">{{ stats.books }}</h3>
                </div>
            </div>

            <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow relative overflow-hidden group">
                <div class="absolute right-0 top-0 w-24 h-24 bg-purple-50 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
                <div class="relative z-10">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2.5 bg-purple-100 text-purple-600 rounded-xl">
                            <Activity class="w-6 h-6" />
                        </div>
                        <span class="flex items-center text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
                            +24% <ArrowUpRight class="w-3 h-3 ml-1" />
                        </span>
                    </div>
                    <p class="text-sm font-medium text-gray-500 mb-1">交互次数</p>
                    <h3 class="text-3xl font-bold text-gray-900">{{ stats.interactions }}</h3>
                </div>
            </div>

            <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow relative overflow-hidden group">
                <div class="absolute right-0 top-0 w-24 h-24 bg-amber-50 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
                <div class="relative z-10">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2.5 bg-amber-100 text-amber-600 rounded-xl">
                            <Star class="w-6 h-6" />
                        </div>
                        <span class="flex items-center text-xs font-medium text-rose-600 bg-rose-50 px-2 py-1 rounded-full">
                            -2% <ArrowDownRight class="w-3 h-3 ml-1" />
                        </span>
                    </div>
                    <p class="text-sm font-medium text-gray-500 mb-1">总评价数</p>
                    <h3 class="text-3xl font-bold text-gray-900">{{ stats.ratings }}</h3>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Main Chart Area (Mockup) -->
            <div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <div class="flex items-center justify-between mb-6">
                    <h3 class="font-bold text-gray-900">用户增长</h3>
                    <select class="text-sm border-gray-200 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-gray-500">
                        <option>过去 7 天</option>
                        <option>过去 30 天</option>
                        <option>今年</option>
                    </select>
                </div>
                <div class="h-64 flex items-end justify-between gap-2 px-2">
                    <div v-for="i in 12" :key="i" class="w-full bg-blue-100 rounded-t-sm hover:bg-blue-200 transition-colors relative group" :style="{ height: `${Math.random() * 80 + 20}%` }">
                        <div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                            {{ Math.floor(Math.random() * 100) }} 用户
                        </div>
                    </div>
                </div>
                <div class="flex justify-between mt-4 text-xs text-gray-400">
                    <span v-for="i in 12" :key="i">{{ i }}月</span>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <h3 class="font-bold text-gray-900 mb-6">最近活动</h3>
                <div class="space-y-6">
                    <div v-for="activity in activities" :key="activity.id" class="flex gap-4">
                        <div class="relative">
                            <div class="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center border border-gray-100">
                                <Star v-if="activity.type === 'rating'" class="w-4 h-4 text-amber-500" />
                                <Users v-else-if="activity.type === 'user'" class="w-4 h-4 text-blue-500" />
                                <BookOpen v-else-if="activity.type === 'collection'" class="w-4 h-4 text-purple-500" />
                                <Activity v-else class="w-4 h-4 text-gray-500" />
                            </div>
                            <div class="absolute top-10 left-1/2 -translate-x-1/2 w-px h-full bg-gray-100 -z-10 last:hidden"></div>
                        </div>
                        <div class="flex-1">
                            <p class="text-sm font-medium text-gray-900">
                                <span class="font-bold">{{ activity.user }}</span> {{ activity.action }} 
                                <span v-if="activity.target" class="text-blue-600">{{ activity.target }}</span>
                            </p>
                            <div class="flex items-center gap-1.5 mt-1 text-xs text-gray-500">
                                <Clock class="w-3 h-3" />
                                {{ activity.time }}
                            </div>
                        </div>
                    </div>
                </div>
                <button class="w-full mt-6 py-2.5 text-sm text-blue-600 font-medium hover:bg-blue-50 rounded-lg transition-colors border border-transparent hover:border-blue-100">
                    查看所有活动
                </button>
            </div>
        </div>
    </div>
  </AdminLayout>
</template>
