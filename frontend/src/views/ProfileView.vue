<template>
  <div class="profile-page">
    <div class="container mt-4 pb-5">
      <div class="profile-card">
        <div class="rank-badge">
          <i class="bi bi-trophy-fill"></i>
          <span>Топ 5</span>
        </div>

        <div class="profile-header">
          <div class="profile-avatar">
            <img v-if="displayedAvatarUrl" :src="displayedAvatarUrl" alt="Аватар">
            <div v-else class="initials-circle">
              {{ userInitials }}
            </div>
          </div>
          <div class="profile-info">
            <h2 class="profile-username">{{ userData?.username || 'Загрузка...' }}</h2>
            <p v-if="userData?.about" class="profile-about">{{ userData.about }}</p>
            <p v-else class="profile-about placeholder" style="cursor: auto; background-color: transparent;">Расскажите о себе...</p>
          </div>
        </div>

        <!-- Секция статистики -->
        <div class="stats-section mt-2">
          <h5 class="section-title mb-3">Статистика чтения</h5>
          
          <div class="stats-grid">
            <div class="stat-item main-stat">
              <div class="stat-icon">
                <i class="bi bi-book-fill"></i>
              </div>
              <div class="stat-content">
                <span class="stat-value">{{ userData?.stats?.read_count ?? 0 }}</span>
                <span class="stat-label">Всего прочитано</span>
              </div>
            </div>
            
            <div class="stat-item">
              <div class="stat-icon">
                <i class="bi bi-bookmark-star-fill"></i>
              </div>
              <div class="stat-content">
                <span class="stat-value">{{ userData?.stats?.progress_marks_count ?? 0 }}</span>
                <span class="stat-label">Всего отметок прогресса</span>
              </div>
            </div>
          </div>

          <div class="history-button-wrapper">
            <button class="btn btn-history" @click="showProgressHistory = true">
              <i class="bi bi-clock-history"></i>
              История отметок прогресса
            </button>
          </div>
        </div>

        <div class="profile-actions">
          <RouterLink to="/profile/lists" class="btn btn-outline-light">
            <i class="bi bi-list-ul"></i>
            Списки
          </RouterLink>
          <RouterLink to="/profile/settings" class="btn btn-outline-light">
            <i class="bi bi-gear"></i>
            Настройки
          </RouterLink>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно истории прогресса -->
    <ProgressHistoryModal 
      v-if="showProgressHistory" 
      @close="showProgressHistory = false" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import type { User } from '@/types';
import { useUserStore } from '@/stores/user';
import { storeToRefs } from 'pinia';
import ProgressHistoryModal from '@/components/ProgressHistoryModal.vue';

const router = useRouter();
const userStore = useUserStore();
const { userData, userInitials, isLoggedIn } = storeToRefs(userStore);
const { fetchUserData } = userStore;

// Состояние модального окна истории прогресса
const showProgressHistory = ref(false);

// Вычисляемое свойство для определения URL отображаемого аватара
const displayedAvatarUrl = computed(() => {
  console.log('ProfileView: Computing displayedAvatarUrl. userData:', userData.value);
  const backendBaseUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
  
  // Используем avatar_url из userData
  if (userData.value?.avatar_url) {
    const url = userData.value.avatar_url;
    console.log('ProfileView: Computed avatar URL:', url);
    return url;
  } else {
    console.log('ProfileView: userData.avatar_url is not set.');
    return ''; // Или URL дефолтной картинки
  }
});

const logout = () => {
  userStore.clearAuthData();
  router.push('/auth/login');
};

// Добавляем явный вызов fetchUserData при монтировании
onMounted(() => {
  console.log('ProfileView: Mounted');
  if (isLoggedIn.value) {
    console.log('ProfileView: User is logged in, fetching data...');
    fetchUserData();
  }
  console.log('ProfileView: Initial userData in store:', userData.value);
});

watch(userData, (newValue, oldValue) => {
  console.log('ProfileView: userData changed:', { oldValue, newValue });
});
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
  position: relative;
}

.rank-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: linear-gradient(45deg, #ffd700, #ffa500);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  display: flex;
  align-items: center;
  font-weight: bold;
  color: #2c3e50;
  box-shadow: 0 2px 10px rgba(255, 215, 0, 0.3);
  z-index: 1;
  gap: 0.5rem;
}

.rank-badge i {
  font-size: 1.2rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid rgba(168, 230, 207, 0.1);
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #a8e6cf;
  box-shadow: 0 0 20px rgba(168, 230, 207, 0.3);
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
  text-decoration: none;
}

.profile-info {
  flex-grow: 1;
}

.profile-username {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
  color: #a8e6cf;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  text-decoration: none;
}

.profile-about {
  color: rgba(255, 255, 255, 0.7);
  margin: 0.5rem 0 0;
  font-size: 1.1rem;
  line-height: 1.6;
}

.profile-about.placeholder {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

.stats-section {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 4rem;
}

.section-title {
  color: #a8e6cf;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.stat-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.stat-item.main-stat {
  background: rgba(168, 230, 207, 0.1);
  border-color: rgba(168, 230, 207, 0.2);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: transparent;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(168, 230, 207, 0.3);
}

.stat-icon i {
  color: #a8e6cf;
  font-size: 1.5rem;
}

.stat-item.main-stat .stat-icon {
  border-color: #a8e6cf;
  background: rgba(168, 230, 207, 0.1);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #a8e6cf;
  line-height: 1;
}

.stat-label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
}

.history-button-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.btn-history {
  background: rgba(168, 230, 207, 0.1);
  border: 1px solid rgba(168, 230, 207, 0.2);
  color: #a8e6cf;
  padding: 1rem 2rem;
  border-radius: 10px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.3s ease;
}

.btn-history:hover {
  background: rgba(168, 230, 207, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.btn-history i {
  font-size: 1.2rem;
}

.profile-actions {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  display: flex;
  gap: 1rem;
}

.profile-actions .btn {
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.profile-actions .btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>