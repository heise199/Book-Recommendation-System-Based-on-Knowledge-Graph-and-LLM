<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UserLayout from '@/layouts/UserLayout.vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { Heart, BookOpen, Star, ArrowLeft, Calendar, Tag, Book, MessageSquare, Send } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const book = ref<any>(null)
const loading = ref(false)
const collecting = ref(false)

const newRating = ref(5)
const newComment = ref('')
const submittingReview = ref(false)

const fetchBook = async () => {
  loading.value = true
  try {
    const res = await axios.get(`/api/books/${route.params.id}`)
    book.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleCollect = async () => {
    if (!authStore.token) {
        router.push('/login')
        return
    }
    
    collecting.value = true
    try {
        await axios.post(`/api/interactions`, {
            book_id: book.value.id,
            interaction_type: 'collect'
        })
        // Show success feedback (could be improved with a toast notification system)
        alert('已加入收藏！')
    } catch (e) {
        console.error(e)
        alert('收藏失败')
    } finally {
        collecting.value = false
    }
}

const handleRead = () => {
    if (!authStore.token) {
        router.push('/login')
        return
    }
    // Mock reading experience
    alert('正在打开阅读器...')
}

const handleReviewSubmit = async () => {
    if (!authStore.token) {
        router.push('/login')
        return
    }
    if (!newComment.value.trim()) {
        alert('请输入评论内容')
        return
    }

    submittingReview.value = true
    try {
        await axios.post(`/api/books/${book.value.id}/rate`, {
            book_id: book.value.id,
            rating: newRating.value,
            comment: newComment.value
        })
        alert('评价成功！')
        newComment.value = ''
        fetchBook() // Refresh to show new review
    } catch (e) {
        console.error(e)
        alert('评价失败，请稍后重试')
    } finally {
        submittingReview.value = false
    }
}

onMounted(fetchBook)
</script>

<template>
  <UserLayout>
    <div v-if="loading" class="flex justify-center items-center min-h-[50vh]">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="book" class="max-w-5xl mx-auto animate-fade-in">
      <!-- Breadcrumb / Back -->
      <button 
        @click="router.back()" 
        class="group flex items-center gap-2 text-sm text-gray-500 hover:text-blue-600 transition-colors mb-6"
      >
        <div class="p-1 rounded-full bg-white border border-gray-200 group-hover:border-blue-200 transition-colors">
            <ArrowLeft class="w-4 h-4" />
        </div>
        <span>返回图书馆</span>
      </button>

      <div class="bg-white rounded-3xl shadow-xl shadow-gray-200/50 overflow-hidden border border-gray-100">
        <div class="md:flex">
          <!-- Cover Image Section -->
          <div class="md:w-2/5 lg:w-1/3 bg-gray-50 relative min-h-[400px] md:min-h-[600px] p-8 flex items-center justify-center">
            <div class="relative w-full max-w-[280px] aspect-[2/3] shadow-2xl rounded-lg overflow-hidden transform transition-transform hover:scale-[1.02] duration-500">
                <img 
                    v-if="book.cover_url" 
                    :src="book.cover_url" 
                    :alt="book.title"
                    class="w-full h-full object-cover"
                />
                <div v-else class="w-full h-full flex flex-col items-center justify-center text-gray-400 bg-white border-2 border-dashed border-gray-200">
                    <Book class="w-16 h-16 mb-4 opacity-20" />
                    <span class="text-sm font-medium uppercase tracking-wider opacity-60">暂无封面</span>
                </div>
            </div>
            
            <!-- Background Blur Effect -->
            <div 
                v-if="book.cover_url"
                class="absolute inset-0 opacity-10 blur-3xl scale-110 pointer-events-none"
                :style="{ backgroundImage: `url(${book.cover_url})`, backgroundSize: 'cover', backgroundPosition: 'center' }"
            ></div>
          </div>

          <!-- Details Section -->
          <div class="md:w-3/5 lg:w-2/3 p-8 lg:p-12 flex flex-col">
            <div class="flex flex-col gap-2 mb-6">
                <div class="flex items-center gap-3 text-sm mb-2">
                    <span v-if="book.category_name" class="px-3 py-1 bg-blue-50 text-blue-700 rounded-full font-medium flex items-center gap-1.5">
                        <Tag class="w-3.5 h-3.5" />
                        {{ book.category_name }}
                    </span>
                    <span v-if="book.publication_year" class="flex items-center gap-1.5 text-gray-500">
                        <Calendar class="w-3.5 h-3.5" />
                        {{ book.publication_year }}
                    </span>
                </div>
                
                <h1 class="text-4xl lg:text-5xl font-bold text-gray-900 leading-tight tracking-tight mb-2">{{ book.title }}</h1>
                <p class="text-xl text-gray-500 font-medium">作者 <span class="text-gray-900">{{ book.author }}</span></p>
            </div>

            <div class="flex items-center gap-6 mb-8 py-6 border-y border-gray-100">
                <div class="flex flex-col">
                    <div class="flex items-center gap-1.5 text-amber-500 mb-1">
                        <div class="flex">
                            <Star 
                                v-for="i in 5" 
                                :key="i" 
                                class="w-6 h-6" 
                                :class="i <= Math.round(book.average_rating || 0) ? 'fill-current text-amber-400' : 'text-gray-200'" 
                            />
                        </div>
                        <span class="text-2xl font-bold text-gray-900 ml-2">{{ book.average_rating?.toFixed(1) || '0.0' }}</span>
                    </div>
                    <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">平均评分</span>
                </div>
                <div class="w-px h-12 bg-gray-100"></div>
                <!-- You could add more stats here like page count, language etc if available -->
                 <div class="flex flex-col">
                    <div class="flex items-center gap-1.5 text-blue-500 mb-1">
                        <BookOpen class="w-6 h-6" />
                        <span class="text-2xl font-bold text-gray-900">中文</span>
                    </div>
                    <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">语言</span>
                </div>
            </div>

            <div class="prose prose-lg prose-slate max-w-none text-gray-600 mb-10 flex-1 leading-relaxed">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">书籍简介</h3>
              <p>{{ book.summary || '暂无书籍简介。' }}</p>
            </div>

            <div class="flex flex-col sm:flex-row gap-4 mt-auto">
              <button 
                  @click="handleRead"
                  class="flex-1 bg-gray-900 text-white px-8 py-4 rounded-xl font-bold hover:bg-gray-800 transition-all transform active:scale-[0.98] flex items-center justify-center gap-3 shadow-lg shadow-gray-900/20"
              >
                  <BookOpen class="w-5 h-5" />
                  立即阅读
              </button>
              <button 
                  @click="handleCollect"
                  :disabled="collecting"
                  class="flex-1 border-2 border-gray-200 text-gray-700 px-8 py-4 rounded-xl font-bold hover:border-gray-900 hover:text-gray-900 transition-all flex items-center justify-center gap-3 bg-white"
              >
                  <Heart class="w-5 h-5 transition-transform group-hover:scale-110" :class="{ 'text-pink-500 fill-current': false }" />
                  加入收藏
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Reviews Section -->
      <div class="mt-12 bg-white rounded-3xl shadow-xl shadow-gray-200/50 p-8 lg:p-12 border border-gray-100">
        <div class="flex items-center gap-3 mb-8">
            <div class="p-2 bg-purple-100 rounded-lg text-purple-600">
                <MessageSquare class="w-6 h-6" />
            </div>
            <h2 class="text-2xl font-bold text-gray-900">读者评论</h2>
        </div>

        <!-- Review Form -->
        <div v-if="authStore.token" class="mb-10 bg-gray-50 p-6 rounded-2xl border border-gray-100">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">发表评论</h3>
            <div class="flex flex-col gap-4">
                <div class="flex items-center gap-2">
                    <span class="text-sm font-medium text-gray-600">您的评分:</span>
                    <div class="flex gap-1">
                        <button 
                            v-for="i in 5" 
                            :key="i"
                            @click="newRating = i"
                            class="focus:outline-none transition-transform hover:scale-110"
                        >
                            <Star 
                                class="w-6 h-6" 
                                :class="i <= newRating ? 'text-amber-400 fill-current' : 'text-gray-300'"
                            />
                        </button>
                    </div>
                </div>
                <textarea 
                    v-model="newComment"
                    rows="3"
                    placeholder="分享您的阅读心得..."
                    class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all resize-none bg-white"
                ></textarea>
                <button 
                    @click="handleReviewSubmit"
                    :disabled="submittingReview"
                    class="self-end px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-500 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <Send class="w-4 h-4" />
                    {{ submittingReview ? '发布中...' : '发布评论' }}
                </button>
            </div>
        </div>
        <div v-else class="mb-10 p-6 bg-gray-50 rounded-2xl text-center border border-gray-100">
            <p class="text-gray-600">请 <router-link to="/login" class="text-blue-600 font-bold hover:underline">登录</router-link> 后发表评论</p>
        </div>

        <!-- Reviews List -->
        <div class="space-y-6">
            <div v-if="book.ratings && book.ratings.length > 0">
                <div v-for="rating in book.ratings" :key="rating.id" class="border-b border-gray-100 last:border-0 pb-6 last:pb-0">
                    <div class="flex justify-between items-start mb-2">
                        <div class="flex items-center gap-2">
                            <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-xs">
                                {{ rating.username ? rating.username.substring(0,2).toUpperCase() : 'U' }}
                            </div>
                            <span class="font-bold text-gray-900">{{ rating.username || '匿名用户' }}</span>
                        </div>
                        <div class="flex text-amber-400">
                            <Star v-for="i in 5" :key="i" class="w-4 h-4" :class="i <= rating.rating ? 'fill-current' : 'text-gray-200'" />
                        </div>
                    </div>
                    <p class="text-gray-600 leading-relaxed">{{ rating.comment }}</p>
                    <p class="text-xs text-gray-400 mt-2">{{ new Date(rating.created_at).toLocaleDateString() }}</p>
                </div>
            </div>
            <div v-else class="text-center py-10 text-gray-500">
                暂无评论，快来抢沙发吧！
            </div>
        </div>
      </div>
    </div>
    
    <div v-else class="flex flex-col items-center justify-center min-h-[50vh] text-center">
        <div class="bg-gray-100 p-6 rounded-full mb-4">
            <Book class="w-12 h-12 text-gray-400" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">未找到书籍</h2>
        <p class="text-gray-500 mb-8">您查找的书籍不存在或已被移除。</p>
        <button @click="router.back()" class="text-blue-600 font-medium hover:underline flex items-center gap-2">
            <ArrowLeft class="w-4 h-4" />
            返回图书馆
        </button>
    </div>
  </UserLayout>
</template>
