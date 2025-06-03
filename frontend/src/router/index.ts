import { createRouter, createWebHistory, type RouteLocationNormalized, type NavigationGuardNext } from 'vue-router'
// import { useUserStore } from '@/stores/user' // Раскомментируем позже

import AuthLayout from '@/layouts/AuthLayout.vue'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import BooksView from '@/views/BooksView.vue'
import ProfileView from '@/views/ProfileView.vue'
import BookDetailView from '@/views/BookDetailView.vue'
import BookReaderView from '@/views/BookReaderView.vue'
import SettingsView from '@/views/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/auth',
      component: AuthLayout,
      children: [
        {
          path: 'login',
          name: 'login',
          component: LoginView
        },
        {
          path: 'register',
          name: 'register',
          component: RegisterView
        }
      ]
    },
    {
      path: '/books',
      name: 'books',
      component: BooksView,
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: '/profile/settings',
      name: 'profile-settings',
      component: SettingsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/books/:id',
      name: 'book-detail',
      component: BookDetailView,
      meta: { requiresAuth: true }
    },
    {
      path: '/books/:id/read',
      name: 'book-reader',
      component: BookReaderView,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach(async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  // const userStore = useUserStore(); // Раскомментируем позже
  const isAuthenticated = !!localStorage.getItem('authToken')

  const requiresAuth = to.matched.some((record: { meta: { requiresAuth?: boolean } }) => record.meta.requiresAuth)

  if (requiresAuth && !isAuthenticated) {
    next({ name: 'login' })
  } else if ((to.name === 'login' || to.name === 'register') && isAuthenticated) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
 