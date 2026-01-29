<script setup lang="ts">
import { ref, onMounted } from 'vue'
import UserLayout from '@/layouts/UserLayout.vue'
import BookCard from '@/components/BookCard.vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { BookMarked, History, User, Mail, Calendar, Edit, Settings } from 'lucide-vue-next'

const authStore = useAuthStore()
const collections = ref<any[]>([])
const loading = ref(false)

const fetchCollections = async () => {
    if (!authStore.token) return
    loading.value = true
    try {
        const res = await axios.get(`/api/users/me/collections`)
        collections.value = res.data
    } catch (error) {
        console.error('Failed to fetch collections', error)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchCollections()
})
</script>

<template>
  <UserLayout>
    <div class="max-w-6xl mx-auto animate-fade-in">
        <!-- Profile Header -->
        <div class="bg-white rounded-3xl shadow-xl shadow-gray-200/50 overflow-hidden mb-12 border border-gray-100">
            <!-- Cover Banner -->
            <div class="h-48 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 relative overflow-hidden">
                <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
                <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
            </div>
            
            <div class="px-8 pb-8">
                <div class="relative flex flex-col md:flex-row justify-between items-end -mt-16 gap-6">
                    <div class="flex flex-col md:flex-row items-center md:items-end gap-6">
                        <!-- Avatar -->
                        <div class="w-32 h-32 bg-white rounded-full p-1.5 shadow-xl ring-4 ring-white/50 relative z-10">
                            <div class="w-full h-full bg-slate-100 rounded-full flex items-center justify-center text-4xl font-bold text-slate-400 overflow-hidden">
                                <span v-if="!authStore.user?.avatar_url">{{ authStore.user?.username?.charAt(0).toUpperCase() }}</span>
                                <img v-else :src="authStore.user.avatar_url" alt="Avatar" class="w-full h-full object-cover" />
                            </div>
                        </div>
                        
                        <!-- User Info -->
                        <div class="text-center md:text-left mb-2">
                            <h1 class="text-3xl font-bold text-gray-900 mb-1">{{ authStore.user?.username }}</h1>
                            <div class="flex flex-wrap items-center justify-center md:justify-start gap-4 text-gray-500 text-sm">
                                <div class="flex items-center gap-1.5">
                                    <Mail class="w-4 h-4" />
                                    <span>{{ authStore.user?.email }}</span>
                                </div>
                                <div class="flex items-center gap-1.5">
                                    <Calendar class="w-4 h-4" />
                                    <span>加入时间 {{ new Date().toLocaleDateString() }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Actions -->
                    <div class="flex gap-3 mb-2 w-full md:w-auto">
                        <button class="flex-1 md:flex-none items-center justify-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm flex">
                            <Settings class="w-4 h-4" />
                            设置
                        </button>
                        <button class="flex-1 md:flex-none items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-all shadow-md shadow-blue-600/20 flex">
                            <Edit class="w-4 h-4" />
                            编辑资料
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
            <!-- Sidebar Stats (Optional) -->
            <div class="hidden lg:block space-y-6">
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <h3 class="font-bold text-gray-900 mb-4">阅读统计</h3>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center">
                            <span class="text-gray-500 text-sm">已读书籍</span>
                            <span class="font-semibold text-gray-900">12</span>
                        </div>
                        <div class="w-full bg-gray-100 rounded-full h-2">
                            <div class="bg-blue-500 h-2 rounded-full" style="width: 45%"></div>
                        </div>
                        
                        <div class="flex justify-between items-center pt-2">
                            <span class="text-gray-500 text-sm">收藏书籍</span>
                            <span class="font-semibold text-gray-900">{{ collections.length }}</span>
                        </div>
                        <div class="w-full bg-gray-100 rounded-full h-2">
                            <div class="bg-purple-500 h-2 rounded-full" style="width: 70%"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="lg:col-span-3 space-y-8">
                <section>
                    <div class="flex items-center justify-between mb-6">
                        <div class="flex items-center gap-3">
                            <div class="p-2 bg-pink-100 rounded-lg text-pink-600">
                                <BookMarked class="w-5 h-5" />
                            </div>
                            <h2 class="text-2xl font-bold text-gray-900">我的收藏</h2>
                        </div>
                        
                        <!-- Filter/Sort placeholder -->
                        <div class="flex gap-2">
                            <select class="text-sm border-gray-200 rounded-lg focus:ring-blue-500 focus:border-blue-500">
                                <option>最近添加</option>
                                <option>书名 (A-Z)</option>
                                <option>评分</option>
                            </select>
                        </div>
                    </div>

                    <div v-if="loading" class="flex justify-center py-20">
                        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
                    </div>
                    
                    <div v-else-if="collections.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        <BookCard v-for="book in collections" :key="book.id" :book="book" />
                    </div>

                    <div v-else class="text-center py-16 bg-white rounded-2xl border-2 border-dashed border-gray-200">
                        <div class="bg-gray-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <BookMarked class="w-8 h-8 text-gray-400" />
                        </div>
                        <h3 class="text-lg font-medium text-gray-900">暂无收藏</h3>
                        <p class="text-gray-500 max-w-sm mx-auto mt-2 mb-6">开始收藏您喜欢的书籍，建立您的个人图书馆。</p>
                        <router-link to="/" class="inline-flex items-center justify-center px-6 py-2.5 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/20">
                            浏览书籍
                        </router-link>
                    </div>
                </section>
            </div>
        </div>
    </div>
  </UserLayout>
</template>
