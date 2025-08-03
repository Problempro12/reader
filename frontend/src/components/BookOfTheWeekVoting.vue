<template>
  <div class="voting-section">
    <h2 class="section-title">Голосование за книгу недели</h2>
    
    <!-- Текущая книга недели -->
    <div v-if="currentBookOfTheWeek" class="current-book mb-4">
      <h3 class="section-subtitle">Текущая книга недели</h3>
      <div class="book-card current">
        <div class="book-cover">
          <img :src="currentBookOfTheWeek.coverUrl" :alt="currentBookOfTheWeek.title" @error="handleImageError">
        </div>
        <div class="book-info">
          <h3 class="book-title">{{ currentBookOfTheWeek.title }}</h3>
          <p class="book-author">{{ currentBookOfTheWeek.author }}</p>
          <div class="book-meta">
            <span class="book-genre">{{ currentBookOfTheWeek.genre?.name }}</span>
            <span class="book-age">{{ currentBookOfTheWeek.ageCategory?.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Кандидаты на книгу недели -->
    <div v-if="candidates.length > 0" class="candidates-section">
      <h3 class="section-subtitle">Выберите книгу на следующую неделю</h3>
      <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
        <div v-for="book in candidates" :key="book.id" class="col">
          <div class="book-card candidate" :class="{ 'voted': hasVoted(book.id) }">
            <div class="book-cover">
              <img :src="book.coverUrl" :alt="book.title" @error="handleImageError">
            </div>
            <div class="book-info">
              <h3 class="book-title">{{ book.title }}</h3>
              <p class="book-author">{{ book.author }}</p>
              <div class="book-meta">
                <span class="book-genre">{{ book.genre?.name }}</span>
                <span class="book-age">{{ book.ageCategory?.name }}</span>
              </div>
              <div class="book-rating">
                <i class="bi bi-star-fill" v-for="n in 5" :key="n" 
                   :class="{ 'active': n <= Math.round(book.rating) }"></i>
                <span>{{ book.rating.toFixed(1) }}</span>
              </div>
              <button class="btn btn-primary w-100 mt-3" 
                      @click="voteForBook(book)"
                      :disabled="hasVoted(book.id)">
                {{ hasVoted(book.id) ? 'Вы уже голосовали' : 'Голосовать' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Нет кандидатов -->
    <div v-else class="no-candidates">
      <p>В данный момент нет доступных книг для голосования</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

interface Book {
  id: number;
  title: string;
  author: string;
  coverUrl: string;
  rating: number;
  genre?: {
    name: string;
  };
  ageCategory?: {
    name: string;
  };
}

const currentBookOfTheWeek = ref<Book | null>(null);
const candidates = ref<Book[]>([]);
const votedBooks = ref<number[]>([]);

const fetchCurrentBook = async () => {
  try {
    const response = await axios.get('/api/books/current-week');
    currentBookOfTheWeek.value = response.data;
  } catch (error) {
    console.error('Ошибка при получении текущей книги недели:', error);
  }
};

const fetchCandidates = async () => {
  try {
    const response = await axios.get('/api/books/voting-candidates');
    candidates.value = response.data;
  } catch (error) {
    console.error('Ошибка при получении кандидатов:', error);
  }
};

const fetchUserVotes = async () => {
  try {
    const response = await axios.get('/api/books/user-votes');
    votedBooks.value = response.data.map((vote: any) => vote.bookId);
  } catch (error) {
    console.error('Ошибка при получении голосов пользователя:', error);
  }
};

const voteForBook = async (book: Book) => {
  try {
    await axios.post('/api/books/votes/', {
      bookId: book.id
    });
    votedBooks.value.push(book.id);
  } catch (error) {
    console.error('Ошибка при голосовании:', error);
  }
};

const hasVoted = (bookId: number) => {
  return votedBooks.value.includes(bookId);
};

// Обработка ошибок загрузки изображений
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  // Предотвращаем бесконечный цикл ошибок
  if (img.src.includes('placeholder-book.svg')) {
    return;
  }
  img.src = '/placeholder-book.svg';
  img.onerror = null; // Убираем обработчик ошибок для заглушки
};

onMounted(() => {
  fetchCurrentBook();
  fetchCandidates();
  fetchUserVotes();
});
</script>

<style scoped>
.voting-section {
  padding: 2rem 0;
}

.section-title {
  color: #a8e6cf;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 2rem;
}

.section-subtitle {
  color: #a8e6cf;
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
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

.book-card.current {
  background: rgba(168, 230, 207, 0.1);
  border-color: rgba(168, 230, 207, 0.3);
}

.book-card.candidate {
  height: 100%;
}

.book-card.voted {
  border-color: #a8e6cf;
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

.book-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.book-rating i {
  color: rgba(255, 255, 255, 0.3);
}

.book-rating i.active {
  color: #ffd700;
}

.book-rating span {
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

.no-candidates {
  text-align: center;
  padding: 3rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  color: rgba(255, 255, 255, 0.7);
}
</style>