<template>
  <div class="profile-page">
    <div class="container mt-4">
      <div class="profile-card">
        <div class="profile-header">
          <div class="profile-avatar">
            <img v-if="userData && userData.avatar" :src="userData.avatar" alt="Аватар">
            <div v-else class="initials-circle">
              {{ userInitials }}
            </div>
          </div>
          <div class="profile-info">
            <h2 class="profile-username">{{ userData?.username || 'Загрузка...' }}</h2>
            <p v-if="userData?.about" class="profile-about">{{ userData.about }}</p>
            <p v-else class="profile-about placeholder">Расскажите о себе...</p>
          </div>
        </div>

        <!-- Секция статистики (будет заполнена данными из бэкенда) -->
        <div class="stats-section mt-4">
          <h5 class="section-title">Статистика чтения</h5>
          <div class="stats-grid">
            <div class="stat-item">
              <i class="bi bi-book"></i>
              <span>Всего книг: {{ userData?.stats?.total_books ?? 0 }}</span>
            </div>
            <div class="stat-item">
              <i class="bi bi-bookmark-check"></i>
              <span>Прочитано: {{ userData?.stats?.completed ?? 0 }}</span>
            </div>
            <div class="stat-item">
              <i class="bi bi-book-half"></i>
              <span>В процессе: {{ userData?.stats?.reading ?? 0 }}</span>
            </div>
            <div class="stat-item">
              <i class="bi bi-heart"></i>
              <span>В желаемом: {{ userData?.stats?.wishlist ?? 0 }}</span>
            </div>
          </div>
        </div>

        <!-- Секция списков книг (будет реализована позже) -->
        <div class="lists-section mt-4">
          <h5 class="section-title">Мои списки</h5>
          <p class="placeholder-text">Здесь будут ваши списки книг...</p>
        </div>

        <div class="profile-actions mt-4">
          <button class="btn btn-primary">
            <i class="bi bi-pencil"></i>
            Редактировать профиль
          </button>
          <button class="btn btn-outline-light">
            <i class="bi bi-gear"></i>
            Настройки
          </button>
          <button class="btn btn-danger" @click="logout">
            <i class="bi bi-box-arrow-right"></i>
            Выйти
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import type { User } from '@/types';
import { useUserStore } from '@/stores/user';
import { storeToRefs } from 'pinia';

const router = useRouter();
const userStore = useUserStore();
const { userData, userInitials, isLoggedIn } = storeToRefs(userStore);

const logout = () => {
  userStore.clearAuthData();
  router.push('/auth/login');
};

// onMounted здесь не нужен для загрузки данных, т.к. это делает сам стор
// при инициализации, если есть токен. Данные будут реактивно обновляться.
</script>

<style scoped>
.profile-page {
  min-height: calc(100vh - var(--header-height, 60px) - var(--footer-height, 60px));
  padding-top: var(--header-height, 60px);
  color: #fff;
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
}

.profile-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 15px;
  padding: 2rem;
  margin-top: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #a8e6cf;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.initials-circle {
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #a8e6cf, #8cd3b0);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2c3e50;
  font-size: 2.5rem;
  font-weight: bold;
}

.profile-info {
  flex-grow: 1;
}

.profile-username {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
  color: #a8e6cf;
}

.profile-about {
  color: rgba(255, 255, 255, 0.7);
  margin: 0.5rem 0 0;
  font-size: 1.1rem;
}

.profile-about.placeholder {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

.profile-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.profile-actions .btn {
  padding: 0.75rem 1.5rem;
  font-weight: 500;
}

.btn-primary {
  background-color: #a8e6cf;
  border-color: #a8e6cf;
  color: #2c3e50;
}

.btn-primary:hover {
  background-color: #8cd3b0;
  border-color: #8cd3b0;
}

.btn-outline-light {
  border-color: rgba(255, 255, 255, 0.3);
}

.btn-outline-light:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.btn-danger {
  background-color: #ff6b6b;
  border-color: #ff6b6b;
}

.btn-danger:hover {
  background-color: #ff5252;
  border-color: #ff5252;
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
  }

  .profile-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}

.stats-section, .lists-section {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 10px;
  padding: 1.5rem;
}

.section-title {
  color: #a8e6cf;
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #fff;
}

.stat-item i {
  color: #a8e6cf;
  font-size: 1.5rem;
}

.placeholder-text {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}
</style> 