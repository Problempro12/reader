<template>
  <div class="auth-page login-page d-flex align-items-center justify-content-center vh-100">
    <div class="auth-container card p-4 p-md-5 shadow-lg">
      <h2 class="text-center mb-4 auth-title">Вход</h2>
      <form @submit.prevent="login">
        <div class="mb-3 form-group-icon">
          <label for="email" class="form-label">Email</label>
          <i class="bi bi-envelope"></i>
          <input type="email" class="form-control" id="email" v-model="email" required>
        </div>
        <div class="mb-3 form-group-icon">
          <label for="password" class="form-label">Пароль</label>
          <i class="bi bi-lock"></i>
          <input type="password" class="form-control" id="password" v-model="password" required>
        </div>
        <button type="submit" class="btn btn-primary w-100 mt-3" :disabled="loading">Войти</button>
        <div v-if="error" class="alert alert-danger mt-3" role="alert">
          {{ error }}
        </div>
      </form>
      <p class="text-center mt-3 mb-0 text-light">
        Нет аккаунта? <RouterLink to="/auth/register" class="auth-link">Зарегистрироваться</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axiosInstance from '@/plugins/axios'
import axios from 'axios'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref<string | null>(null)
const router = useRouter()
const userStore = useUserStore()
const route = useRoute()

const login = async () => {
  loading.value = true
  error.value = null
  console.log('=== Начало процесса входа ===')
  console.log('Email:', email.value)
  console.log('Параметры запроса:', route.query)
  
  try {
    console.log('Отправка запроса на сервер...')
    const response = await axiosInstance.post('users/login/', {
      email: email.value,
      password: password.value
    })
    
    console.log('Ответ от сервера:', response.data)
    console.log('Проверка полей пользователя:', {
      hasUser: !!response.data.user,
      is_staff: response.data.user?.is_staff,
      is_superuser: response.data.user?.is_superuser
    })
    
    // Проверяем наличие полей is_staff и is_superuser
    if (!response.data.user || typeof response.data.user.is_staff === 'undefined' || typeof response.data.user.is_superuser === 'undefined') {
      console.error('Отсутствуют поля is_staff или is_superuser в ответе сервера')
      error.value = 'Ошибка авторизации: отсутствуют необходимые данные'
      return
    }
    
    console.log('Сохранение данных в localStorage...')
    // Сохраняем токены в localStorage
    localStorage.setItem('authToken', response.data.token)
    localStorage.setItem('refreshToken', response.data.refresh)
    localStorage.setItem('user', JSON.stringify(response.data.user))
    
    // Проверяем, что данные сохранились правильно
    const savedUser = JSON.parse(localStorage.getItem('user') || '{}')
    console.log('Сохраненные данные пользователя:', savedUser)
    console.log('Проверка прав администратора:', {
      is_staff: savedUser.is_staff,
      is_superuser: savedUser.is_superuser
    })
    
    console.log('Обновление состояния store...')
    // Обновляем состояние store
    userStore.setAuthData(response.data.token, response.data.user)
    
    // Проверяем данные в store
    console.log('Данные в store после обновления:', {
      userData: userStore.userData,
      isAdmin: userStore.userData?.is_staff || userStore.userData?.is_superuser
    })
    
    // Перенаправляем на предыдущий маршрут или на главную
    const redirectPath = route.query.redirect as string || '/'
    console.log('Перенаправление на:', redirectPath)
    router.push(redirectPath)
  } catch (error) {
    console.error('Ошибка при входе:', error)
    if (axios.isAxiosError(error)) {
      console.error('Детали ошибки:', {
        status: error.response?.status,
        data: error.response?.data,
        headers: error.response?.headers
      })
    }
    error.value = 'Неверный email или пароль'
  } finally {
    loading.value = false
    console.log('=== Конец процесса входа ===')
  }
}
</script>

<style scoped>
.auth-page {
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
  color: #fff;
}

.auth-container {
  background: rgba(255, 255, 255, 0.08); /* Немного меньше прозрачности */
  backdrop-filter: blur(10px);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 15px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
  flex-shrink: 0;
  animation: fadeInScale 0.6s ease-out forwards; /* Добавляем анимацию */
}

.auth-title {
  color: #a8e6cf;
  font-weight: bold;
  font-size: 2rem;
}

.form-label {
  color: #a8e6cf;
  margin-bottom: 0.25rem;
}

.form-group-icon {
  position: relative;
}

.form-group-icon i {
  position: absolute;
  left: 15px;
  top: 65%; /* Позиционируем иконку */
  transform: translateY(-50%);
  color: rgba(168, 230, 207, 0.7);
  pointer-events: none; /* Иконка не должна перехватывать события мыши */
  z-index: 2;
}

.form-control {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  outline: none !important;
  padding-left: 40px; /* Увеличиваем padding для иконки */
  transition: all 0.3s ease;
}

.form-control:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: #a8e6cf;
  box-shadow: 0 0 0 0.25rem rgba(168, 230, 207, 0.25);
  color: #fff;
}

.form-control::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.btn-primary {
  background: #a8e6cf;
  border-color: #a8e6cf;
  color: #2c3e50;
  font-weight: bold;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: #8cd3b0;
  border-color: #8cd3b0;
  transform: translateY(-2px);
}

.auth-link {
  color: #a8e6cf;
  text-decoration: none;
  transition: color 0.3s ease;
}

.auth-link:hover {
  text-decoration: underline;
  color: #8cd3b0;
}

/* Анимация появления */
@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style> 