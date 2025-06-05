<template>
  <div class="profile-page">
    <div class="container mx-auto px-4 py-8">
      <div class="max-w-4xl mx-auto">
        <!-- Профиль -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div class="flex items-center space-x-6">
            <!-- Аватар -->
            <div class="w-24 h-24 rounded-full bg-primary flex items-center justify-center text-3xl font-bold text-white">
              {{ userData?.username?.charAt(0).toUpperCase() }}
            </div>
            
            <!-- Информация -->
            <div>
              <h1 class="text-3xl font-bold text-gray-900">{{ userData?.username }}</h1>
              <p class="text-gray-600">{{ userData?.email }}</p>
            </div>
          </div>
        </div>

        <!-- Статистика -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="bg-white rounded-lg shadow-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Читаю сейчас</h3>
            <p class="text-3xl font-bold text-primary">{{ userData?.stats?.reading || 0 }}</p>
          </div>
          <div class="bg-white rounded-lg shadow-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Прочитано</h3>
            <p class="text-3xl font-bold text-green-600">{{ userData?.stats?.completed || 0 }}</p>
          </div>
          <div class="bg-white rounded-lg shadow-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-2">В планах</h3>
            <p class="text-3xl font-bold text-blue-600">{{ userData?.stats?.planned || 0 }}</p>
          </div>
        </div>

        <!-- Кнопки действий -->
        <div class="flex justify-end space-x-4">
          <button 
            @click="logout" 
            class="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Выйти
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

const router = useRouter()
const userStore = useUserStore()
const { userData } = storeToRefs(userStore)

onMounted(async () => {
  await userStore.fetchUserData()
})

const logout = () => {
  userStore.clearAuthData()
  router.push('/login')
}
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
}

.profile-actions .btn {
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
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