import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // User Routes
    {
      path: '/',
      name: 'home',
      component: () => import('@/pages/user/HomePage.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/auth/UserLogin.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/pages/auth/UserRegister.vue')
    },
    {
      path: '/book/:id',
      name: 'book-detail',
      component: () => import('@/pages/user/BookDetail.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/pages/user/UserProfile.vue'),
      meta: { requiresAuth: true }
    },
    
    // Admin Routes
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/pages/auth/AdminLogin.vue')
    },
    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: () => import('@/pages/admin/AdminDashboard.vue'),
      meta: { requiresAdmin: true }
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('@/pages/admin/UserManagement.vue'),
      meta: { requiresAdmin: true }
    },
    {
      path: '/admin/books',
      name: 'admin-books',
      component: () => import('@/pages/admin/BookManagement.vue'),
      meta: { requiresAdmin: true }
    },

    // Catch all
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// Navigation Guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check for admin routes
  if (to.meta.requiresAdmin) {
    if (!authStore.token || !authStore.isAdmin) {
      return next('/admin/login')
    }
  }
  
  // Check for authenticated user routes
  if (to.meta.requiresAuth) {
    if (!authStore.token) {
      return next('/login')
    }
  }
  
  next()
})

export default router
