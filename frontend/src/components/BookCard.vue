<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Star, Book } from 'lucide-vue-next'

const props = defineProps<{
  book: {
    id: number
    title: string
    author: string
    cover_url?: string
    average_rating?: number
    category_name?: string
  }
}>()

const API_URL = 'http://localhost:8000'

const getImageUrl = (url?: string) => {
  if (!url) return null
  if (url.startsWith('http')) return url
  return `${API_URL}${url}`
}

const router = useRouter()

const navigateToDetail = () => {
  router.push(`/book/${props.book.id}`)
}
</script>

<template>
  <div 
    class="group relative bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 ease-out border border-gray-100 overflow-hidden cursor-pointer h-full flex flex-col hover:-translate-y-1"
    @click="navigateToDetail"
  >
    <!-- Image Container -->
    <div class="aspect-[2/3] bg-gray-100 relative overflow-hidden">
      <img 
        v-if="book.cover_url" 
        :src="getImageUrl(book.cover_url)" 
        :alt="book.title"
        loading="lazy"
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" 
      />
      <div v-else class="w-full h-full flex flex-col items-center justify-center text-gray-400 bg-gray-50 p-4 text-center">
        <Book class="w-12 h-12 mb-2 opacity-20" />
        <span class="text-xs font-medium uppercase tracking-wider opacity-60">暂无封面</span>
      </div>
      
      <!-- Overlay Gradient -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      
      <!-- Category Badge -->
      <div v-if="book.category_name" class="absolute top-3 left-3">
        <span class="px-2.5 py-1 bg-white/90 backdrop-blur-md text-gray-900 text-[10px] font-bold uppercase tracking-wider rounded-md shadow-sm border border-white/20">
          {{ book.category_name }}
        </span>
      </div>
    </div>
    
    <!-- Content -->
    <div class="p-4 flex flex-col flex-1">
      <div class="mb-1 flex items-start justify-between gap-2">
        <h3 class="font-bold text-gray-900 leading-tight line-clamp-2 group-hover:text-blue-600 transition-colors" :title="book.title">
          {{ book.title }}
        </h3>
      </div>
      
      <p class="text-sm text-gray-500 mb-3 font-medium">{{ book.author }}</p>
      
      <div class="mt-auto flex items-center justify-between border-t border-gray-50 pt-3">
        <div class="flex items-center gap-1">
          <div class="flex">
            <Star 
              v-for="i in 5" 
              :key="i" 
              class="w-3 h-3" 
              :class="i <= Math.round(book.average_rating || 0) ? 'fill-amber-400 text-amber-400' : 'text-gray-200'" 
            />
          </div>
          <span class="text-xs font-bold text-gray-500 ml-1">{{ book.average_rating?.toFixed(1) || '0.0' }}</span>
        </div>
        <span class="text-xs font-semibold text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-2 group-hover:translate-x-0 duration-300">
          查看详情
        </span>
      </div>
    </div>
  </div>
</template>
