<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import UserLayout from '@/layouts/UserLayout.vue'
import BookCard from '@/components/BookCard.vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { Sparkles, Library, Loader2, Search, ArrowRight } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const recommendations = ref<any[]>([])
const books = ref<any[]>([])
const loadingRecs = ref(false)
const loadingBooks = ref(false)
const searchQuery = ref('')
const selectedCategory = ref<string | ''>('')
const viewingAll = ref(false)

const fetchRecommendations = async () => {
  if (!authStore.user?.id) {
    if (authStore.token) {
      await authStore.fetchUser()
      if (!authStore.user?.id) return
    } else {
      return
    }
  }
  
  loadingRecs.value = true
  try {
    const res = await axios.get(`/api/recommend/${authStore.user.id}`)
    recommendations.value = res.data
  } catch (error) {
    console.error('Failed to fetch recommendations:', error)
  } finally {
    loadingRecs.value = false
  }
}

const handleViewAll = async () => {
  if (viewingAll.value) return

  loadingBooks.value = true
  try {
    const res = await axios.get(`/api/books?limit=200`)
    books.value = res.data
    viewingAll.value = true
  } catch (error) {
    console.error('Failed to fetch all books:', error)
  } finally {
    loadingBooks.value = false
  }
}

const handleSearch = async () => {
  const q = searchQuery.value.trim()

  if (!q && !selectedCategory.value) {
    fetchBooks()
    return
  }

  if (!authStore.token) {
    router.push('/login')
    return
  }

  loadingBooks.value = true
  try {
    const payload: any = { query: q || '' }
    if (selectedCategory.value) {
      payload.category_name = selectedCategory.value
    }

    const res = await axios.post(
      `/api/search`,
      payload
    )
    books.value = res.data
    viewingAll.value = false
  } catch (error) {
    console.error('Failed to search books:', error)
  } finally {
    loadingBooks.value = false
  }
}

const fetchBooks = async () => {
  loadingBooks.value = true
  try {
    const res = await axios.get(`/api/books?limit=12`)
    books.value = res.data
  } catch (error) {
    console.error('Failed to fetch books:', error)
  } finally {
    loadingBooks.value = false
  }
}

onMounted(() => {
  if (authStore.token) {
    fetchRecommendations()
  }
  fetchBooks()
})
</script>

<template>
  <UserLayout>
    <div class="space-y-16">
      <!-- Hero Section -->
      <section class="relative overflow-hidden rounded-3xl bg-gray-900 text-white shadow-2xl">
        <div class="absolute inset-0">
          <img 
            src="https://images.unsplash.com/photo-1481627834876-b7833e8f5570?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80" 
            alt="Library" 
            class="h-full w-full object-cover opacity-30"
          />
          <div class="absolute inset-0 bg-gradient-to-r from-gray-900 via-gray-900/80 to-transparent"></div>
        </div>
        
        <div class="relative px-6 py-16 sm:px-12 sm:py-24 lg:py-32">
          <div class="max-w-2xl">
            <h1 class="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl mb-6">
              发现您的下一场 <br/>
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">文学冒险</span>
            </h1>
            <p class="mt-6 text-lg leading-8 text-gray-300 max-w-xl">
              探索为您精心挑选的海量书籍。通过我们的 AI 智能推荐引擎，只需点击一下，即可找到您最喜爱的下一个故事。
            </p>
            <div class="mt-10 flex items-center gap-x-6">
              <a href="#library" class="rounded-full bg-blue-600 px-8 py-3.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 transition-all flex items-center gap-2">
                开始探索 <ArrowRight class="w-4 h-4" />
              </a>
              <a href="#" class="text-sm font-semibold leading-6 text-white hover:text-blue-300 transition-colors">了解更多 <span aria-hidden="true">→</span></a>
            </div>
          </div>
        </div>
      </section>

      <!-- Recommendations Section -->
      <section v-if="authStore.token" class="animate-fade-in">
        <div class="flex items-center justify-between mb-8">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-amber-100 rounded-lg text-amber-600">
              <Sparkles class="w-6 h-6" />
            </div>
            <div>
              <h2 class="text-2xl font-bold text-gray-900">为您推荐</h2>
              <p class="text-sm text-gray-500">基于您的阅读历史</p>
            </div>
          </div>
        </div>
        
        <div v-if="loadingRecs" class="flex justify-center py-20">
          <Loader2 class="w-10 h-10 animate-spin text-blue-600" />
        </div>
        
        <div v-else-if="recommendations.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-8">
          <div v-for="(rec, index) in recommendations" :key="index" class="relative group h-full">
            <BookCard :book="rec.book" />
            <!-- Recommendation Reason Tooltip/Badge -->
            <div class="absolute -top-2 -right-2 z-10 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
              <div class="bg-gray-900 text-white text-xs py-1.5 px-3 rounded-lg shadow-lg max-w-[200px]">
                <span class="font-bold text-amber-400 block mb-0.5">推荐理由：</span>
                {{ rec.reason }}
              </div>
              <div class="w-2 h-2 bg-gray-900 rotate-45 absolute bottom-0 left-4 -mb-1"></div>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center py-16 bg-white rounded-2xl border-2 border-dashed border-gray-200">
          <div class="bg-gray-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search class="w-8 h-8 text-gray-400" />
          </div>
          <h3 class="text-lg font-medium text-gray-900">暂无推荐</h3>
          <p class="text-gray-500 max-w-sm mx-auto mt-2">多与书籍互动，帮助我们的 AI 更好地了解您的口味！</p>
        </div>
      </section>

      <!-- All Books Section -->
      <section id="library" class="animate-slide-up">
        <div class="flex items-center justify-between mb-8">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-emerald-100 rounded-lg text-emerald-600">
              <Library class="w-6 h-6" />
            </div>
            <div>
              <h2 class="text-2xl font-bold text-gray-900">探索图书馆</h2>
              <p class="text-sm text-gray-500">发现最新上架的书籍</p>
            </div>
          </div>
          
          <div class="flex items-center gap-3">
            <select
              v-model="selectedCategory"
              class="hidden sm:block text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white text-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            >
              <option value="">全部分类</option>
              <option value="科幻">科幻</option>
              <option value="历史">历史</option>
              <option value="计算机">计算机</option>
              <option value="经济管理">经济管理</option>
              <option value="心理学">心理学</option>
              <option value="悬疑">悬疑</option>
            </select>
            <div class="relative w-40 sm:w-64">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="按书名或作者搜索..."
                class="w-full pl-9 pr-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                @keyup.enter="handleSearch"
              />
            </div>
            <button
              class="text-sm font-medium px-3 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
              @click="handleSearch"
            >
              搜索
            </button>
            <button
              class="text-sm font-medium hover:underline"
              :class="viewingAll ? 'text-gray-400 cursor-not-allowed' : 'text-blue-600 hover:text-blue-700'"
              :disabled="viewingAll"
              @click="handleViewAll"
            >
              {{ viewingAll ? '已显示全部' : '查看所有书籍' }}
            </button>
          </div>
        </div>
        
        <div v-if="loadingBooks" class="flex justify-center py-20">
          <Loader2 class="w-10 h-10 animate-spin text-blue-600" />
        </div>
        
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6 sm:gap-8">
          <BookCard v-for="book in books" :key="book.id" :book="book" />
        </div>
      </section>
    </div>
  </UserLayout>
</template>
