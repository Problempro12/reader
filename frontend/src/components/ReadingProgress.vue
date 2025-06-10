<template>
  <div class="reading-progress">
    <h2 class="section-title">Отметка прогресса чтения</h2>
    
    <!-- Текущая книга недели -->
    <div v-if="currentBook" class="current-book mb-4">
      <div class="book-card">
        <div class="book-cover">
          <img :src="currentBook.coverUrl" :alt="currentBook.title">
        </div>
        <div class="book-info">
          <h3 class="book-title">{{ currentBook.title }}</h3>
          <p class="book-author">{{ currentBook.author }}</p>
          <div class="book-meta">
            <span class="book-genre">{{ currentBook.genre?.name }}</span>
            <span class="book-age">{{ currentBook.ageCategory?.name }}</span>
          </div>
          <div class="progress-info">
            <p>Ваши отметки: {{ userMarks }}</p>
            <p>Всего отметок: {{ totalMarks }}</p>
          </div>
          <button 
            class="btn btn-primary w-100 mt-3" 
            @click="markProgress"
            :disabled="isMarkingDisabled"
          >
            {{ buttonText }}
          </button>
        </div>
      </div>
    </div>

    <!-- Нет текущей книги -->
    <div v-else class="no-book">
      <p>В данный момент нет активной книги недели</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

interface Book {
  id: number;
  title: string;
  author: string;
  coverUrl: string;
  genre?: {
    name: string;
  };
  ageCategory?: {
    name: string;
  };
}

const currentBook = ref<Book | null>(null);
const userMarks = ref(0);
const totalMarks = ref(0);
const lastMarkTime = ref<Date | null>(null);
const isMarkingDisabled = ref(false);

const buttonText = computed(() => {
  if (!currentBook.value) return 'Нет активной книги';
  if (isMarkingDisabled.value) return 'Подождите 15 минут';
  return 'Отметить 15 минут чтения';
});

const fetchCurrentBook = async () => {
  try {
    const response = await axios.get('/api/books/current-week');
    currentBook.value = response.data;
    if (currentBook.value) {
      await fetchProgress();
    }
  } catch (error) {
    console.error('Ошибка при получении текущей книги:', error);
  }
};

const fetchProgress = async () => {
  if (!currentBook.value) return;
  
  try {
    const response = await axios.get(`/api/books/progress/${currentBook.value.id}`);
    userMarks.value = response.data.userMarks;
    totalMarks.value = response.data.totalMarks;
  } catch (error) {
    console.error('Ошибка при получении прогресса:', error);
  }
};

const markProgress = async () => {
  if (!currentBook.value || isMarkingDisabled.value) return;
  
  try {
    await axios.post('/api/books/progress/', {
      bookId: currentBook.value.id
    });
    
    // Обновляем время последней отметки
    lastMarkTime.value = new Date();
    isMarkingDisabled.value = true;
    
    // Обновляем прогресс
    await fetchProgress();
    
    // Разблокируем кнопку через 15 минут
    setTimeout(() => {
      isMarkingDisabled.value = false;
    }, 15 * 60 * 1000);
  } catch (error) {
    console.error('Ошибка при отметке прогресса:', error);
  }
};

onMounted(() => {
  fetchCurrentBook();
});
</script>

<style scoped>
.reading-progress {
  padding: 2rem 0;
}

.section-title {
  color: #a8e6cf;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 2rem;
}

.book-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 15px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.book-cover {
  width: 100%;
  height: 300px;
  overflow: hidden;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-info {
  padding: 1.5rem;
}

.book-title {
  font-size: 1.25rem;
  font-weight: bold;
  margin: 0 0 0.5rem;
  color: #fff;
}

.book-author {
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 1rem;
}

.book-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.book-genre,
.book-age {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.7);
}

.progress-info {
  margin: 1rem 0;
  color: rgba(255, 255, 255, 0.7);
}

.btn-primary {
  background: linear-gradient(45deg, #a8e6cf, #8cd3b0);
  border: none;
  color: #1a1a1a;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(45deg, #8cd3b0, #a8e6cf);
  transform: translateY(-2px);
}

.btn-primary:disabled {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
}

.no-book {
  text-align: center;
  padding: 3rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  color: rgba(255, 255, 255, 0.7);
}
</style> 