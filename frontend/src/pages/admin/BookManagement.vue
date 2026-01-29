<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { Plus, Search, MoreVertical, Edit, Trash2, Book, Filter } from 'lucide-vue-next'

const authStore = useAuthStore()
const books = ref<any[]>([])
const loading = ref(false)
const searchQuery = ref('')

const fetchBooks = async () => {
  loading.value = true
  try {
    const res = await axios.get(`/api/books?limit=50`)
    books.value = res.data
  } catch (error) {
    console.error('Failed to fetch books:', error)
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id: number) => {
    if (!confirm('您确定要删除这本书吗？')) return
    // Mock delete for now as API might not support it yet
    console.log('Delete book', id)
    // Refresh list
    // fetchBooks()
}

onMounted(fetchBooks)
</script>

<template>
  <AdminLayout>
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">图书管理</h1>
        <p class="text-gray-500 text-sm mt-1">管理图书馆藏书和目录。</p>
      </div>
      <button class="flex items-center gap-2 bg-blue-600 text-white px-4 py-2.5 rounded-lg hover:bg-blue-700 shadow-lg shadow-blue-600/20 transition-all font-medium text-sm">
        <Plus class="w-4 h-4" />
        添加新书
      </button>
    </div>

    <!-- Filters & Search -->
    <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 mb-6 flex flex-col sm:flex-row gap-4 justify-between items-center">
        <div class="relative w-full sm:w-96">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input 
                v-model="searchQuery"
                type="text" 
                placeholder="按书名、作者或 ISBN 搜索..." 
                class="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
        </div>
        <div class="flex gap-2 w-full sm:w-auto">
            <button class="flex items-center gap-2 px-4 py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                <Filter class="w-4 h-4" />
                筛选
            </button>
        </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-gray-50 border-b border-gray-200">
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider w-16">
                        <input type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                    </th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">书籍信息</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">分类</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">评分</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">出版年份</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">操作</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                <tr v-if="loading">
                    <td colspan="6" class="px-6 py-12 text-center">
                        <div class="flex justify-center">
                             <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        </div>
                    </td>
                </tr>
                <tr v-else-if="books.length === 0">
                    <td colspan="6" class="px-6 py-12 text-center text-gray-500">
                        没有找到符合条件的书籍。
                    </td>
                </tr>
                <tr v-for="book in books" :key="book.id" class="hover:bg-gray-50/50 transition-colors group">
                    <td class="px-6 py-4">
                        <input type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                    </td>
                    <td class="px-6 py-4">
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-16 bg-gray-100 rounded flex-shrink-0 overflow-hidden border border-gray-200">
                                <img v-if="book.cover_url" :src="book.cover_url" class="w-full h-full object-cover" />
                                <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                                    <Book class="w-6 h-6" />
                                </div>
                            </div>
                            <div>
                                <h3 class="text-sm font-semibold text-gray-900 line-clamp-1">{{ book.title }}</h3>
                                <p class="text-xs text-gray-500">{{ book.author }}</p>
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-4">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                            {{ book.category_name || '未分类' }}
                        </span>
                    </td>
                    <td class="px-6 py-4">
                        <div class="flex items-center gap-1 text-sm text-gray-900">
                            <span class="font-medium">{{ book.average_rating?.toFixed(1) || '0.0' }}</span>
                            <span class="text-xs text-gray-400">/ 5</span>
                        </div>
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-500">
                        {{ book.publication_year || '未知' }}
                    </td>
                    <td class="px-6 py-4 text-right">
                        <div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button class="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors" title="编辑">
                                <Edit class="w-4 h-4" />
                            </button>
                            <button @click="handleDelete(book.id)" class="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors" title="删除">
                                <Trash2 class="w-4 h-4" />
                            </button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
      </div>
      
      <!-- Pagination (Static Mockup) -->
      <div class="px-6 py-4 border-t border-gray-100 flex items-center justify-between">
          <div class="text-sm text-gray-500">
              显示第 <span class="font-medium text-gray-900">1</span> 到 <span class="font-medium text-gray-900">10</span> 条，共 <span class="font-medium text-gray-900">50</span> 条结果
          </div>
          <div class="flex gap-2">
              <button disabled class="px-3 py-1 text-sm border border-gray-200 rounded text-gray-400 bg-gray-50 cursor-not-allowed">上一页</button>
              <button class="px-3 py-1 text-sm border border-gray-200 rounded text-gray-600 hover:bg-gray-50">下一页</button>
          </div>
      </div>
    </div>
  </AdminLayout>
</template>
