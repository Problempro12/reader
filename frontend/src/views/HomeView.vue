<script setup lang="ts">
import { ref, onMounted, defineComponent } from 'vue'
import { RouterLink } from 'vue-router'

import masterImg from '@/assets/books/мастер-и-маргарита.webp';
import crimeImg from '@/assets/books/преступление-и-наказание.jpg';
import warImg from '@/assets/books/война-и-мир-2.jpg';
import BookOfTheWeekVoting from '@/components/BookOfTheWeekVoting.vue';

defineComponent({
  name: 'HomeView'
})

// Временные данные для демонстрации
const featuredBooks = ref([
  {
    id: 1,
    title: 'Война и мир',
    author: 'Лев Толстой',
    cover: 'https://via.placeholder.com/400x600/2c3e50/ffffff?text=Война+и+мир',
    progress: 45,
    rating: 4.8,
    genre: 'Классика',
    description: 'Величайший роман о любви, войне и поисках смысла жизни'
  },
  {
    id: 2,
    title: 'Преступление и наказание',
    author: 'Фёдор Достоевский',
    cover: 'https://via.placeholder.com/400x600/34495e/ffffff?text=Преступление+и+наказание',
    progress: 78,
    rating: 4.9,
    genre: 'Психологический роман',
    description: 'Глубокое исследование человеческой души и морали'
  },
  {
    id: 3,
    title: 'Мастер и Маргарита',
    author: 'Михаил Булгаков',
    cover: 'https://via.placeholder.com/400x600/2c3e50/ffffff?text=Мастер+и+Маргарита',
    progress: 23,
    rating: 4.7,
    genre: 'Фэнтези',
    description: 'Мистический роман о любви, творчестве и вечных ценностях'
  }
])

const readingStats = ref({
  booksRead: 12,
  pagesRead: 3456,
  readingStreak: 7,
  totalTime: 45
})

const isVisible = ref(false)

onMounted(() => {
  isVisible.value = true
})
</script>

<template>
  <div class="home-page">
    <!-- Приветственный баннер (вынесен за .container) -->
    <div class="hero-section w-100">
      <div class="row align-items-center min-vh-75 m-0">
        <div class="col-lg-6 px-5 d-flex flex-column justify-content-center" :class="{ 'fade-in': isVisible }">
          <h1 class="display-3 fw-bold mb-4 text-gradient">Добро пожаловать в мир чтения</h1>
          <p class="lead mb-4">Откройте для себя новые горизонты, погрузитесь в увлекательные истории и станьте частью нашего читательского сообщества.</p>
          <div class="d-flex gap-3">
            <RouterLink to="/app/books" class="btn btn-primary btn-lg px-4 py-2">
              Начать читать
              <i class="bi bi-arrow-right ms-2"></i>
            </RouterLink>
            <RouterLink to="/auth/register" class="btn btn-outline-light btn-lg px-4 py-2">
              Присоединиться
            </RouterLink>
          </div>
        </div>
        <div class="col-lg-6 d-none d-lg-block position-relative">
          <div class="floating-books">
            <img :src="masterImg" alt="Книга" class="book-1">
            <img :src="crimeImg" alt="Книга" class="book-2">
            <img :src="warImg" alt="Книга" class="book-3">
          </div>
          <div style="position: absolute; bottom: -20px; right: 24px; z-index: 10; min-width: 320px;">
            <BookOfTheWeekVoting />
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Статистика чтения -->
      <div class="stats-section py-5">
        <div class="row g-4">
          <div class="col-md-3" v-for="(stat, index) in Object.entries(readingStats)" :key="index">
            <div class="stat-card" :class="{ 'fade-in': isVisible }" :style="{ '--delay': index * 0.2 + 's' }">
              <div class="stat-icon">
                <i :class="[
                  'bi',
                  index === 0 ? 'bi-book' : 
                  index === 1 ? 'bi-file-text' :
                  index === 2 ? 'bi-calendar-check' :
                  'bi-clock'
                ]"></i>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">{{ stat[1] }}</h3>
                <p class="stat-label">{{ 
                  index === 0 ? 'Прочитано книг' :
                  index === 1 ? 'Прочитано страниц' :
                  index === 2 ? 'Дней подряд' :
                  'Часов чтения'
                }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Рекомендуемые книги -->
      <div class="books-section py-5">
        <div class="container">
          <h2 class="section-title mb-5">Продолжить чтение</h2>
          <div class="row g-4">
            <div v-for="book in featuredBooks" :key="book.id" class="col-md-4">
              <div class="book-card" :class="{ 'fade-in': isVisible }">
                <div class="book-cover">
                  <img :src="book.cover" :alt="book.title">
                  <div class="book-overlay">
                    <RouterLink :to="`/app/books/${book.id}`" class="btn btn-light">
                      Читать
                    </RouterLink>
                  </div>
                </div>
                <div class="book-info">
                  <div class="book-genre">{{ book.genre }}</div>
                  <h3 class="book-title">{{ book.title }}</h3>
                  <p class="book-author">{{ book.author }}</p>
                  <p class="book-description">{{ book.description }}</p>
                  <div class="book-progress">
                    <div class="progress">
                      <div class="progress-bar" role="progressbar" 
                           :style="{ width: book.progress + '%' }" 
                           :aria-valuenow="book.progress" 
                           aria-valuemin="0" 
                           aria-valuemax="100">
                      </div>
                    </div>
                    <span class="progress-text">{{ book.progress }}%</span>
                  </div>
                  <div class="book-rating">
                    <i class="bi bi-star-fill"></i>
                    <span>{{ book.rating }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
  color: #fff;
}

.hero-section {
  min-height: 80vh;
  background: linear-gradient(135deg, rgba(44, 62, 80, 0.9) 0%, rgba(52, 73, 94, 0.9) 100%);
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('https://images.unsplash.com/photo-1507842217343-583bb7270b66?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80') center/cover;
  opacity: 0.1;
  z-index: 0;
}

.text-gradient {
  background: linear-gradient(45deg, #fff, #a8e6cf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.floating-books {
  position: relative;
  height: 500px;
}

.floating-books img {
  position: absolute;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  transition: transform 0.3s ease;
  width: 100px;
  object-fit: cover;
}

.book-1 {
  top: 0;
  left: 0;
  transform: rotate(-5deg);
  z-index: 3;
}

.book-2 {
  top: 50px;
  left: 100px;
  transform: rotate(5deg);
  z-index: 2;
}

.book-3 {
  top: 100px;
  left: 200px;
  transform: rotate(-3deg);
  z-index: 1;
}

.floating-books img:hover {
  transform: translateY(-10px) rotate(0deg);
  z-index: 4;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transition: transform 0.3s ease;
  opacity: 0;
  animation: fadeIn 0.5s ease forwards;
  animation-delay: var(--delay);
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 2.5rem;
  color: #a8e6cf;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
}

.stat-label {
  color: #a8e6cf;
  margin: 0;
}

.book-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  overflow: hidden;
  transition: transform 0.3s ease;
  opacity: 0;
  animation: fadeIn 0.5s ease forwards;
}

.book-card:hover {
  transform: translateY(-10px);
}

.book-cover {
  position: relative;
  overflow: hidden;
}

.book-cover img {
  width: 100%;
  height: 400px;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.book-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.book-card:hover .book-overlay {
  opacity: 1;
}

.book-card:hover .book-cover img {
  transform: scale(1.1);
}

.book-info {
  padding: 1.5rem;
}

.book-genre {
  color: #a8e6cf;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.book-title {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.book-author {
  color: #a8e6cf;
  margin-bottom: 1rem;
}

.book-description {
  font-size: 0.9rem;
  color: #ccc;
  margin-bottom: 1rem;
}

.book-progress {
  margin-bottom: 1rem;
}

.progress {
  height: 6px;
  background: rgba(255,255,255,0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar {
  background: #a8e6cf;
}

.progress-text {
  font-size: 0.8rem;
  color: #a8e6cf;
}

.book-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ffd700;
}

.section-title {
  font-size: 2.5rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 3px;
  background: #a8e6cf;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.5s ease forwards;
}

@media (max-width: 768px) {
  .hero-section {
    min-height: 60vh;
  }
  
  .floating-books {
    display: none;
  }
  
  .stat-card {
    padding: 1.5rem;
  }
  
  .stat-icon {
    font-size: 2rem;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
}
</style>
 