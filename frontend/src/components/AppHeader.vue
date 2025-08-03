<template>
  <nav class="navbar navbar-expand-lg" :class="{ 'navbar-scrolled': isScrolled }">
    <div class="container">
      <RouterLink class="navbar-brand" to="/">
        <i class="bi bi-book-half me-2"></i>
        KpitReading
      </RouterLink>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        @click="isMenuOpen = !isMenuOpen"
        :aria-expanded="isMenuOpen"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" :class="{ show: isMenuOpen }">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <RouterLink class="nav-link" to="/books">
              <i class="bi bi-collection me-1"></i>
              Книги
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/profile">
              <i class="bi bi-person me-1"></i>
              Профиль
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/achievements">
              <i class="bi bi-trophy me-1"></i>
              Достижения
            </RouterLink>
          </li>
        </ul>
        
        <div class="d-flex align-items-center gap-3">
          <div class="search-box">
            <i class="bi bi-search" @click="handleSearch"></i>
            <input 
              type="text" 
              placeholder="Поиск книг..." 
              class="form-control"
              v-model="searchQuery"
              @keyup.enter="handleSearch"
            >
          </div>
          
          <div class="nav-buttons" v-if="!isLoggedIn">
            <RouterLink to="/auth/login" class="btn btn-outline-light">
              <i class="bi bi-box-arrow-in-right me-1"></i>
              Войти
            </RouterLink>
            <RouterLink to="/auth/register" class="btn btn-primary">
              <i class="bi bi-person-plus me-1"></i>
              Регистрация
            </RouterLink>
          </div>
          
          <RouterLink to="/profile" class="user-profile" v-else>
            <div class="user-avatar">
              <img v-if="displayedAvatarUrl" :src="displayedAvatarUrl" alt="Аватар">
              <div v-else class="initials-circle">
                {{ userInitials }}
              </div>
            </div>
            <span class="user-nickname" v-if="userData">{{ userData.username }}</span>
          </RouterLink>

        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia';
import axios from 'axios';

const isMenuOpen = ref(false)
const isScrolled = ref(false)
const searchQuery = ref('')
const userStore = useUserStore()
const router = useRouter()

// Используем storeToRefs для сохранения реактивности при деструктурировании
const { isLoggedIn, userData, userInitials } = storeToRefs(userStore);
const { fetchUserData } = userStore;

const route = useRoute()

onMounted(() => {
  console.log('AppHeader: Mounted');
  window.addEventListener('scroll', () => {
    isScrolled.value = window.scrollY > 50
  })
  // Проверяем скролл при монтировании
  isScrolled.value = window.scrollY > 50
  if (isLoggedIn.value) {
    console.log('AppHeader: User is logged in, fetching data...');
    fetchUserData();
  } else {
    console.log('AppHeader: User is not logged in.');
  }
  console.log('AppHeader: Initial userData in store:', userData.value);
})

watch(route, () => {
  // Сбрасываем состояние прокрутки при смене маршрута (опционально)
  isScrolled.value = false;
})

watch(userData, (newValue, oldValue) => {
  console.log('AppHeader: userData changed:', { oldValue, newValue });
  console.log('AppHeader: displayedAvatarUrl after userData change:', displayedAvatarUrl.value);
});

// Watch isLoggedIn as well, as it triggers fetchUserData
watch(isLoggedIn, (newValue, oldValue) => {
    console.log('AppHeader: isLoggedIn changed:', { oldValue, newValue });
    if (newValue && !oldValue) {
        console.log('AppHeader: isLoggedIn changed to true, fetching data...');
        fetchUserData();
    }
});

// Функция для обработки поиска
const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      path: '/books',
      query: { search: searchQuery.value.trim() }
    });
    searchQuery.value = ''; // Очищаем поле после поиска
  }
};

// Вычисляемое свойство для определения URL отображаемого аватара
const displayedAvatarUrl = computed(() => {
  console.log('AppHeader: Computing displayedAvatarUrl. userData:', userData.value);
  // const backendBaseUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000'; // Удаляем неиспользуемую переменную
  // Используем avatar_url из стора, который теперь формируется на бэкенде
  if (userData.value?.avatar_url) {
    const url = userData.value.avatar_url;
    console.log('AppHeader: Computed avatar URL:', url);
    return url;
  } else {
    console.log('AppHeader: userData.avatar_url is not set.');
    // Возвращаем пустую строку или URL дефолтной картинки, если аватара нет
    return '';
  }
});

const handleAvatarUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    const formData = new FormData()
    formData.append('avatar', file)

    const response = await axios.patch('/api/users/profile/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data) {
      userData.value = response.data
    }
  } catch (error) {
    console.error('Ошибка при загрузке аватара:', error)
    // Можно добавить уведомление пользователю об ошибке
  }
}

// TODO: Добавить функцию логаута
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 1rem 0;
  transition: all 0.3s ease;
  background: transparent;
}

.navbar-scrolled {
  background: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(10px);
  padding: 0.5rem 0;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
  font-size: 2rem;
  font-weight: 800;
  color: #fff;
  text-decoration: none;
  display: flex;
  align-items: left;
  font-family: 'Arial', sans-serif;
  letter-spacing: 1.5px;
  
  background: linear-gradient(45deg, #a8e6cf, #ffffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-fill-color: transparent;
}

.navbar-brand i {
  color: #a8e6cf;
}

.nav-link {
  color: #fff !important;
  font-weight: 500;
  padding: 0.5rem 1rem;
  transition: all 0.3s ease;
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: #a8e6cf;
  transition: width 0.3s ease;
}

.nav-link:hover::after {
  width: 100%;
}

.nav-link i {
  color: #a8e6cf;
}

.search-box {
  position: relative;
  margin-right: 1rem;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #a8e6cf;
  cursor: pointer;
  transition: color 0.3s ease;
}

.search-box i:hover {
  color: #8cd3b0;
}

.search-box input {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 20px;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  color: #fff;
  width: 200px;
  transition: all 0.3s ease;
}

.search-box input:focus {
  background: rgba(255, 255, 255, 0.15);
  width: 250px;
  outline: none;
  box-shadow: none;
}

.search-box input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.nav-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-outline-light {
  border-color: rgba(255, 255, 255, 0.2);
}

.btn-outline-light:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.btn-primary {
  background: #a8e6cf;
  border-color: #a8e6cf;
  color: #2c3e50;
}

.btn-primary:hover {
  background: #8cd3b0;
  border-color: #8cd3b0;
  transform: translateY(-2px);
}

.navbar-toggler {
  border: none;
  padding: 0.5rem;
}

.navbar-toggler:focus {
  box-shadow: none;
}

.navbar-toggler-icon {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='rgba(255, 255, 255, 0.7)' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
}

/* Новые стили для профиля пользователя в хедере */
.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: #fff;
  transition: color 0.3s ease;
}

.user-profile:hover {
  color: #a8e6cf;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(45deg, #a8e6cf, #8cd3b0);
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #a8e6cf; /* Пастельная рамка */
}

.initials-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(45deg, #a8e6cf, #8cd3b0);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2c3e50;
  font-weight: bold;
  font-size: 1rem;
}

.user-nickname {
  /* Дополнительные стили, если нужны */
}

@media (max-width: 991px) {
  .navbar {
    background: rgba(26, 26, 26, 0.95);
    backdrop-filter: blur(10px);
  }
  
  .search-box {
    margin: 1rem 0;
    width: 100%;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .search-box input:focus {
    width: 100%;
  }
  
  .nav-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .btn {
    width: 100%;
    margin: 0.25rem 0;
  }
}
</style>