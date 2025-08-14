<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">
          <i class="bi bi-clock-history"></i>
          История отметок прогресса
        </h3>
        <button class="close-btn" @click="closeModal">
          <i class="bi bi-x"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Загрузка истории...</p>
        </div>
        
        <div v-else-if="progressHistory.length === 0" class="empty-state">
          <i class="bi bi-bookmark-x"></i>
          <p>У вас пока нет отметок прогресса</p>
        </div>
        
        <div v-else class="progress-list">
          <div 
            v-for="progress in progressHistory" 
            :key="progress.id"
            class="progress-item"
          >
            <div class="progress-book">
              <img 
                v-if="progress.user_book?.book?.cover_url" 
                :src="progress.user_book.book.cover_url" 
                :alt="progress.user_book.book.title"
                class="book-cover"
              >
              <div v-else class="book-cover-placeholder">
                <i class="bi bi-book"></i>
              </div>
              
              <div class="book-info">
                <h4 class="book-title">{{ progress.user_book?.book?.title || 'Неизвестная книга' }}</h4>
                <p class="book-author">{{ progress.user_book?.book?.author?.name || 'Неизвестный автор' }}</p>
              </div>
            </div>
            
            <div class="progress-details">
              <div class="progress-stats">
                <span class="progress-page">
                  Страница {{ progress.current_page }} из {{ progress.total_pages }}
                </span>
                <span class="progress-percentage">
                  {{ Math.round(progress.progress_percentage) }}%
                </span>
              </div>
              
              <div class="progress-date">
                <i class="bi bi-calendar3"></i>
                {{ formatDate(progress.created_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="closeModal">
          Закрыть
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getReadingProgress } from '@/api/books';

interface ProgressItem {
  id: number;
  user_book: {
    book: {
      id: number;
      title: string;
      cover_url: string;
      author: {
        name: string;
      };
    };
  };
  current_page: number;
  total_pages: number;
  progress_percentage: number;
  created_at: string;
}

const emit = defineEmits<{
  close: [];
}>();

const loading = ref(true);
const progressHistory = ref<ProgressItem[]>([]);

const closeModal = () => {
  emit('close');
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const loadProgressHistory = async () => {
  try {
    loading.value = true;
    const data = await getReadingProgress();
    progressHistory.value = data.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  } catch (error) {
    console.error('Ошибка загрузки истории прогресса:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadProgressHistory();
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: #1a1a1a;
  border: 1px solid rgba(168, 230, 207, 0.2);
  border-radius: 15px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(168, 230, 207, 0.1);
}

.modal-title {
  color: #a8e6cf;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: rgba(255, 255, 255, 0.7);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(168, 230, 207, 0.3);
  border-top: 3px solid #a8e6cf;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: rgba(255, 255, 255, 0.5);
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: rgba(168, 230, 207, 0.3);
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.progress-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  gap: 1.5rem;
  align-items: center;
  transition: all 0.3s ease;
}

.progress-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(168, 230, 207, 0.2);
}

.progress-book {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.book-cover {
  width: 60px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid rgba(168, 230, 207, 0.2);
}

.book-cover-placeholder {
  width: 60px;
  height: 80px;
  background: rgba(168, 230, 207, 0.1);
  border: 1px solid rgba(168, 230, 207, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(168, 230, 207, 0.5);
  font-size: 1.5rem;
}

.book-info {
  flex: 1;
}

.book-title {
  color: #fff;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  line-height: 1.3;
}

.book-author {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin: 0;
}

.progress-details {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.progress-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.progress-page {
  color: #a8e6cf;
  font-weight: 600;
  font-size: 0.95rem;
}

.progress-percentage {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.progress-date {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(168, 230, 207, 0.1);
  display: flex;
  justify-content: flex-end;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

@media (max-width: 768px) {
  .modal-content {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }
  
  .progress-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .progress-details {
    align-items: flex-start;
    width: 100%;
  }
  
  .progress-stats {
    align-items: flex-start;
  }
}
</style>