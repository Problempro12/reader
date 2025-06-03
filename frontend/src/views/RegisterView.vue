<template>
  <div class="auth-page register-page d-flex align-items-center justify-content-center vh-100">
    <div class="auth-container card p-4 p-md-5 shadow-lg">
      <h2 class="text-center mb-4 auth-title">Регистрация</h2>
      <form @submit.prevent="register">
        <div class="mb-3 form-group-icon">
          <label for="username" class="form-label">Имя пользователя</label>
          <i class="bi bi-person"></i>
          <input type="text" class="form-control" id="username" v-model="username" required>
        </div>
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
        <div class="mb-3 form-group-icon">
          <label for="password2" class="form-label">Подтвердите пароль</label>
          <i class="bi bi-lock"></i>
          <input type="password" class="form-control" id="password2" v-model="password2" required>
        </div>
        <button type="submit" class="btn btn-primary w-100 mt-3" :disabled="loading">Зарегистрироваться</button>
      </form>
      <p class="text-center mt-3 mb-0 text-light">
        Уже есть аккаунт? <RouterLink to="/auth/login" class="auth-link">Войти</RouterLink>
      </p>
      <div v-if="error" class="text-danger text-center mt-3">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import axios from 'axios'

const username = ref('')
const email = ref('')
const password = ref('')
const password2 = ref('')

const router = useRouter()
const error = ref<string | null>(null)
const loading = ref(false)

const register = async () => {
  error.value = null
  loading.value = true

  try {
    const response = await axios.post('http://localhost:8000/api/users/register/', {
      username: username.value,
      email: email.value,
      password: password.value,
      password2: password2.value,
    })

    console.log('Регистрация успешна:', response.data)
    router.push('/auth/login')

  } catch (err: any) {
    console.error('Registration failed:', err)
    if (axios.isAxiosError(err) && err.response && err.response.data) {
      const backendErrors = err.response.data
      let errorMessages = ''
      for (const field in backendErrors) {
        if (Array.isArray(backendErrors[field])) {
          errorMessages += `${field}: ${backendErrors[field].join(', ')}\n`
        } else {
          errorMessages += `${field}: ${backendErrors[field]}\n`
        }
      }
      error.value = errorMessages.trim() || 'Ошибка регистрации. Пожалуйста, попробуйте снова.'
    } else {
      error.value = 'Произошла ошибка при попытке регистрации.'
    }
  } finally {
    loading.value = false
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