<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { Search, MoreVertical, Edit, Trash2, User, Shield, Mail, CheckCircle, XCircle } from 'lucide-vue-next'

const authStore = useAuthStore()
const users = ref<any[]>([])
const loading = ref(false)
const searchQuery = ref('')

const fetchUsers = async () => {
  loading.value = true
  try {
    // const res = await axios.get(`/api/users`)
    // users.value = res.data
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800))
    
    users.value = [
        { id: 1, username: 'admin', email: 'admin@example.com', role: 'admin', status: 'active', joined: '2023-01-15' },
        { id: 2, username: 'alice', email: 'alice@example.com', role: 'user', status: 'active', joined: '2023-02-20' },
        { id: 3, username: 'bob', email: 'bob@example.com', role: 'user', status: 'inactive', joined: '2023-03-10' },
        { id: 4, username: 'charlie', email: 'charlie@example.com', role: 'user', status: 'active', joined: '2023-04-05' },
    ]
  } catch (error) {
    console.error('Failed to fetch users:', error)
  } finally {
    loading.value = false
  }
}

const handleDelete = (id: number) => {
    if (!confirm('您确定要删除这个用户吗？')) return
    console.log('Delete user', id)
}

onMounted(fetchUsers)
</script>

<template>
  <AdminLayout>
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">用户管理</h1>
        <p class="text-gray-500 text-sm mt-1">管理用户账户和权限。</p>
      </div>
      <button class="flex items-center gap-2 bg-gray-900 text-white px-4 py-2.5 rounded-lg hover:bg-gray-800 shadow-lg shadow-gray-900/20 transition-all font-medium text-sm">
        <User class="w-4 h-4" />
        添加新用户
      </button>
    </div>

    <!-- Filters & Search -->
    <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 mb-6 flex flex-col sm:flex-row gap-4 justify-between items-center">
        <div class="relative w-full sm:w-96">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input 
                v-model="searchQuery"
                type="text" 
                placeholder="按姓名或邮箱搜索用户..." 
                class="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
        </div>
        <div class="flex gap-2 w-full sm:w-auto">
             <select class="px-4 py-2.5 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 focus:ring-2 focus:ring-blue-500">
                <option value="all">所有角色</option>
                <option value="admin">管理员</option>
                <option value="user">用户</option>
             </select>
             <select class="px-4 py-2.5 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 focus:ring-2 focus:ring-blue-500">
                <option value="all">所有状态</option>
                <option value="active">活跃</option>
                <option value="inactive">非活跃</option>
             </select>
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
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">用户</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">角色</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">状态</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">加入日期</th>
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
                <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50/50 transition-colors group">
                    <td class="px-6 py-4">
                        <input type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                    </td>
                    <td class="px-6 py-4">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-100 to-indigo-100 text-blue-600 flex items-center justify-center font-bold text-sm">
                                {{ user.username.charAt(0).toUpperCase() }}
                            </div>
                            <div>
                                <h3 class="text-sm font-semibold text-gray-900">{{ user.username }}</h3>
                                <div class="flex items-center gap-1 text-xs text-gray-500">
                                    <Mail class="w-3 h-3" />
                                    {{ user.email }}
                                </div>
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-4">
                        <div class="flex items-center gap-1.5">
                            <Shield v-if="user.role === 'admin'" class="w-4 h-4 text-purple-600" />
                            <User v-else class="w-4 h-4 text-gray-400" />
                            <span class="text-sm text-gray-700 capitalize">{{ user.role === 'admin' ? '管理员' : '用户' }}</span>
                        </div>
                    </td>
                    <td class="px-6 py-4">
                        <span 
                            class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium"
                            :class="user.status === 'active' ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-600'"
                        >
                            <CheckCircle v-if="user.status === 'active'" class="w-3 h-3" />
                            <XCircle v-else class="w-3 h-3" />
                            <span class="capitalize">{{ user.status === 'active' ? '活跃' : '非活跃' }}</span>
                        </span>
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-500">
                        {{ new Date(user.joined).toLocaleDateString() }}
                    </td>
                    <td class="px-6 py-4 text-right">
                        <div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button class="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors" title="编辑">
                                <Edit class="w-4 h-4" />
                            </button>
                            <button @click="handleDelete(user.id)" class="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors" title="删除">
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
              显示第 <span class="font-medium text-gray-900">1</span> 到 <span class="font-medium text-gray-900">4</span> 条，共 <span class="font-medium text-gray-900">4</span> 条结果
          </div>
          <div class="flex gap-2">
              <button disabled class="px-3 py-1 text-sm border border-gray-200 rounded text-gray-400 bg-gray-50 cursor-not-allowed">上一页</button>
              <button disabled class="px-3 py-1 text-sm border border-gray-200 rounded text-gray-400 bg-gray-50 cursor-not-allowed">下一页</button>
          </div>
      </div>
    </div>
  </AdminLayout>
</template>
