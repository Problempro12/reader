import { createRouter, createWebHistory, type RouteLocationNormalized, type NavigationGuardNext } from 'vue-router'
import { useUserStore } from '@/stores/user'

import AuthLayout from '@/layouts/AuthLayout.vue'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import BooksView from '@/views/BooksView.vue'
import ProfileView from '@/views/ProfileView.vue'
import BookDetailView from '@/views/BookDetailView.vue'
import BookReaderView from '@/views/BookReaderView.vue'
import SettingsView from '@/views/SettingsView.vue'
import UserListsView from '@/views/UserListsView.vue'
import PrivacyPolicyView from '@/views/PrivacyPolicyView.vue'
import AchievementsView from '@/views/AchievementsView.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import AdminBooksView from '@/views/admin/BooksView.vue'
import TermsOfUseView from '@/views/TermsOfUseView.vue'
import ContactView from '@/views/ContactView.vue'


const router = createRouter({
  history: createWebHistory(),
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
      path: '/profile/lists',
      name: 'profile-lists',
      component: UserListsView,
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
    },
    {
      path: '/achievements',
      name: 'achievements',
      component: AchievementsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/privacy-policy',
      name: 'privacy-policy',
      component: PrivacyPolicyView,
      meta: { requiresAuth: false }
    },
    {
      path: '/terms',
      name: 'terms',
      component: TermsOfUseView,
      meta: { requiresAuth: false }
    },
    {
      path: '/contact',
      name: 'contact',
      component: ContactView,
      meta: { requiresAuth: false }
    },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'admin-books',
          component: AdminBooksView
        }
      ]
    }
  ],
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach(async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const userStore = useUserStore();
  const isAuthenticated = !!localStorage.getItem('authToken')
  const userData = JSON.parse(localStorage.getItem('user') || '{}')

  console.log('=== Начало проверки прав доступа ===')
  console.log('Текущий маршрут:', to.path)
  console.log('Предыдущий маршрут:', from.path)
  console.log('Параметры запроса:', to.query)
  console.log('Данные пользователя:', {
    isAuthenticated,
    userData,
    token: localStorage.getItem('authToken') ? 'Присутствует' : 'Отсутствует',
    refreshToken: localStorage.getItem('refreshToken') ? 'Присутствует' : 'Отсутствует'
  })
  console.log('Требования маршрута:', {
    requiresAuth: to.matched.some((record: { meta: { requiresAuth?: boolean } }) => record.meta.requiresAuth)
  })

  const requiresAuth = to.matched.some((record: { meta: { requiresAuth?: boolean } }) => record.meta.requiresAuth)

  if (requiresAuth) {
    if (!isAuthenticated) {
      console.log('Требуется аутентификация, перенаправление на страницу входа')
      next({ 
        name: 'login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // Проверяем валидность токена
    try {
      await userStore.fetchUserData()
    } catch (error) {
      console.log('Токен недействителен, перенаправление на страницу входа')
      userStore.clearAuthData()
      next({ 
        name: 'login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }

  if ((to.name === 'login' || to.name === 'register') && isAuthenticated) {
    console.log('Пользователь уже авторизован, перенаправление на главную')
    next({ name: 'home' })
  } else {
    console.log('Доступ разрешен, переход к запрошенному маршруту')
    next()
  }
  console.log('=== Конец проверки прав доступа ===')
})

export default router
 