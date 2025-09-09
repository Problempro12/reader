<script setup lang="ts">
import { ref, onMounted, defineComponent } from 'vue'
import { RouterLink } from 'vue-router'
import { getUserBooks, getPageProgress, getReadingStats } from '@/api/books'
import { useUserStore } from '@/stores/user'

import masterImg from '@/assets/books/мастер-и-маргарита.webp';
import crimeImg from '@/assets/books/преступление-и-наказание.jpg';
import warImg from '@/assets/books/война-и-мир-2.jpg';

const floatingBooks = [
  { src: masterImg, alt: 'Книга', class: 'book-1' },
  { src: crimeImg, alt: 'Книга', class: 'book-2' },
  { src: warImg, alt: 'Книга', class: 'book-3' },
  { src: 'https://cdn.ast.ru/v2/ASE000000000720964/COVER/cover1__w220.jpg', alt: 'Книга', class: 'book-4' },
  { src: 'https://imo10.labirint.ru/books/1010835/cover.jpg/363-0', alt: 'Книга', class: 'book-5' },
  { src: 'https://imo10.labirint.ru/books/1008048/cover.jpg/363-0', alt: 'Книга', class: 'book-6' },
  { src: 'https://cdn.ast.ru/v2/ASE000000000702015/COVER/cover1__w220.jpg', alt: 'Книга', class: 'book-7' },
  { src: 'https://imo10.labirint.ru/books/1003201/cover.jpg/363-0', alt: 'Книга', class: 'book-8' },
  { src: 'https://content.img-gorod.ru/pim/products/images/9b/c5/018fa161-0a98-75ce-9798-9ef8cde59bc5.jpg?width=300&height=300', alt: 'Книга', class: 'book-9' },
  { src: 'https://spbcult.ru/upload/iblock/f3e/287cclmhcmxz249sxui2ocmfpxrxmw7l.jpeg', alt: 'Книга', class: 'book-10' },
  { src: 'https://s1-listing.ozstatic.by/400400/230/330/101/101330230_0.jpg', alt: 'Книга', class: 'book-11' },
];
import TopBooksVoting from '@/components/TopBooksVoting.vue';
import BookOfWeek from '@/components/BookOfWeek.vue';

defineComponent({
  name: 'HomeView',
  components: {
    TopBooksVoting,
    BookOfWeek,
  },
})

// Интерфейс для книги с прогрессом
interface BookWithProgress {
  id: number;
  title: string;
  author: string;
  cover: string;
  progress: number;
  rating: number;
  genre: string;
  description: string;
}

// Данные для книг, которые пользователь читает
const featuredBooks = ref<BookWithProgress[]>([])
const isLoadingBooks = ref(false)
const booksError = ref<string | null>(null)

const readingStats = ref({
  booksRead: 0,
  pagesRead: 0,
  readingStreak: 0,
  totalTime: 0
})
const isLoadingStats = ref(false)
const statsError = ref<string | null>(null)

const isVisible = ref(false)

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

// Функция загрузки книг пользователя
const loadUserReadingBooks = async () => {
  try {
    isLoadingBooks.value = true
    booksError.value = null
    
    // Получаем книги пользователя со статусом "reading"
    const userBooks = await getUserBooks('reading')
    
    // Преобразуем данные и получаем прогресс для каждой книги
    const booksWithProgress = await Promise.all(
      userBooks.slice(0, 3).map(async (userBook: any) => {
        try {
          const progress = await getPageProgress(userBook.book.id)
          return {
            id: userBook.book.id,
            title: userBook.book.title,
            author: userBook.book.author?.name || 'Неизвестный автор',
            cover: userBook.book.cover_url || '/placeholder-book.svg',
            progress: Math.round(progress.progress_percentage || 0),
            rating: userBook.book.rating || 0,
            genre: userBook.book.genre || 'Без жанра',
            description: userBook.book.description || 'Описание отсутствует'
          }
        } catch (error) {
          console.error(`Ошибка получения прогресса для книги ${userBook.book.id}:`, error)
          return {
            id: userBook.book.id,
            title: userBook.book.title,
            author: userBook.book.author?.name || 'Неизвестный автор',
            cover: userBook.book.cover_url || '/placeholder-book.svg',
            progress: 0,
            rating: userBook.book.rating || 0,
            genre: userBook.book.genre || 'Без жанра',
            description: userBook.book.description || 'Описание отсутствует'
          }
        }
      })
    )
    
    featuredBooks.value = booksWithProgress
  } catch (error) {
    console.error('Ошибка загрузки книг пользователя:', error)
    booksError.value = 'Не удалось загрузить книги'
    featuredBooks.value = []
  } finally {
    isLoadingBooks.value = false
  }
}

// Функция загрузки статистики пользователя
const loadUserStats = async () => {
  try {
    isLoadingStats.value = true
    statsError.value = null
    
    // Получаем улучшенную статистику чтения
    const stats = await getReadingStats()
    
    // Обновляем статистику с реальными данными
    readingStats.value = {
      booksRead: stats.books_read,
      pagesRead: stats.pages_read,
      readingStreak: stats.reading_streak,
      totalTime: stats.total_hours
    }
  } catch (error) {
    console.error('Ошибка загрузки статистики:', error)
    statsError.value = 'Не удалось загрузить статистику'
    
    // Fallback: оставляем нулевые значения
    readingStats.value = {
      booksRead: 0,
      pagesRead: 0,
      readingStreak: 0,
      totalTime: 0
    }
  } finally {
    isLoadingStats.value = false
  }
}

onMounted(async () => {
  isVisible.value = true
  await Promise.all([
    loadUserReadingBooks(),
    loadUserStats()
  ])
})

const userStore = useUserStore()
</script>

<template>
  <div class="home-page">
    <!-- Приветственный баннер (вынесен за .container) -->
    <div class="hero-section w-100 position-relative">
      <div class="hero-main-content">
        <div class="row h-100 m-0">
          <div class="col-lg-7 px-5 d-flex flex-column justify-content-start" :class="{ 'fade-in': isVisible }">
            <h1 class="display-3 fw-bold mb-4 text-gradient">Добро пожаловать в мир чтения</h1>
            <p class="lead mb-4">Откройте для себя новые горизонты, погрузитесь в увлекательные истории и станьте частью нашего читательского сообщества.</p>
            <div class="d-flex gap-3">
              <RouterLink to="/books" class="btn start-reading-button px-4 py-2" style="font-family: 'Arial Black', sans-serif;">
                Начать читать
                <i class="bi bi-arrow-right ms-2"></i>
              </RouterLink>
              <RouterLink v-if="!userStore.isLoggedIn" to="/auth/register" class="btn btn-outline-light btn-lg px-4 py-2">
                Присоединиться
              </RouterLink>
            </div>
          </div>
          <div class="col-lg-5 d-none d-lg-block position-relative">
            <div class="floating-books">
              <img v-for="(book, index) in floatingBooks" :key="index" :src="book.src" :alt="book.alt" :class="book.class">
            </div>
          </div>
        </div>
      </div>
      <!-- Книга недели и блок голосования в самом низу hero-секции -->
      <div class="hero-bottom-section">
        <div class="row g-4 m-0">
          <div class="col-lg-7 px-5 d-flex align-items-end">
              <BookOfWeek />
            </div>
          <div class="col-lg-5">
            <TopBooksVoting />
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
          
          <!-- Загрузка -->
          <div v-if="isLoadingBooks" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Загрузка...</span>
            </div>
            <p class="mt-3 text-muted">Загрузка ваших книг...</p>
          </div>
          
          <!-- Ошибка -->
          <div v-else-if="booksError" class="alert alert-warning text-center">
            <i class="bi bi-exclamation-triangle me-2"></i>
            {{ booksError }}
            <button @click="loadUserReadingBooks" class="btn btn-outline-primary btn-sm ms-3">
              <i class="bi bi-arrow-clockwise me-1"></i>
              Повторить
            </button>
          </div>
          
          <!-- Нет книг в процессе чтения -->
          <div v-else-if="featuredBooks.length === 0" class="text-center py-5">
            <i class="bi bi-book text-muted" style="font-size: 3rem;"></i>
            <h4 class="mt-3 text-muted">У вас пока нет книг в процессе чтения</h4>
            <p class="text-muted">Добавьте книги в свою библиотеку и начните читать</p>
            <RouterLink to="/books" class="btn btn-primary">
              <i class="bi bi-search me-2"></i>
              Найти книги
            </RouterLink>
          </div>
          
          <!-- Книги -->
          <div v-else class="row g-4">
            <div v-for="book in featuredBooks" :key="book.id" class="col-md-4">
              <div class="book-card" :class="{ 'fade-in': isVisible }">
                <div class="book-cover">
                  <img :src="book.cover" :alt="book.title" @error="handleImageError">
                  <div class="book-overlay">
                    <RouterLink :to="`/books/${book.id}/read`" class="btn btn-light">
                      Читать
                    </RouterLink>
                  </div>
                </div>
                <div class="book-info">
                  <div class="book-genre">{{ book.genre }}</div>
                  <h3 class="book-title">{{ book.title }}</h3>
                  <p class="book-author">{{ book.author }}</p>
                  <p class="book-description">{{ book.description.length > 80 ? book.description.substring(0, 80) + '...' : book.description }}</p>
                  <div class="book-progress mb-3">
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
                  <div class="d-flex justify-content-between align-items-center">
                    <div class="book-rating" v-if="book.rating > 0">
                      <i class="bi bi-star-fill"></i>
                      <span>{{ book.rating }}</span>
                    </div>
                    <RouterLink :to="`/books/${book.id}/read`" class="btn btn-gradient btn-sm">
                       <i class="bi bi-play-circle-fill me-1"></i>
                       Продолжить
                     </RouterLink>
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
  min-height: 100vh;
  background: linear-gradient(135deg, rgba(44, 62, 80, 0.9) 0%, rgba(52, 73, 94, 0.9) 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.hero-main-content {
  flex: 1;
  display: flex;
  align-items: flex-start;
  padding-top: 80px;
  min-height: calc(100vh - 120px);
}

.hero-bottom-section {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  z-index: 10;
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
  height: 300px;
  margin-top: -120px;
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
  transform: rotate(0deg);
  z-index: 1;
}

.book-4 {
  top: 120px;
  left: 300px;
  transform: rotate(7deg);
  z-index: 0;
}

.book-5 {
  top:135px;
  left: 400px;
  transform: rotate(-6deg);
  z-index: 3;
}

.book-6 {
  top: 135px;
  left: 500px;
  transform: rotate(2deg);
  z-index: 2;
}

.book-7 {
  top: 125px;
  left: 600px;
  transform: rotate(-3deg);
  z-index: 1;
}

.book-8 {
  top: 105px;
  left: 700px;
  transform: rotate(3deg);
  z-index: 0
}

.book-9 {
  top: 85px;
  left: 800px;
  transform: rotate(-2deg);
  z-index: 3;
}

.book-10 {
  top: 55px;
  left: 900px;
  transform: rotate(4deg);
  z-index: 2;
}

.book-11 {
  top: 30px;
  left: 1000px;
  transform: rotate(7deg);
  z-index: 0;
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

.btn-gradient {
  background: linear-gradient(45deg, #a8e6cf, #7fcdcd);
  border: none;
  color: #1a1a1a;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 25px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(168, 230, 207, 0.3);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.btn-gradient:hover {
  background: linear-gradient(45deg, #7fcdcd, #a8e6cf);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(168, 230, 207, 0.4);
  color: #1a1a1a;
  text-decoration: none;
}

.btn-gradient:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(168, 230, 207, 0.3);
}
.start-reading-button {
  background: linear-gradient(45deg, var(--primary-color), #7ed9b2);
  color: var(--primary-dark);
  border: none;
  box-shadow: 0 4px 15px rgba(168, 230, 207, 0.4);
  position: relative;
  overflow: hidden;
  z-index: 1;
  padding: 15px 30px;
  font-size: 1.65rem;
  border-radius: 10px;
  transition: all 0.3s ease; /* Добавляем плавный переход */
}

.start-reading-button:hover {
  background: linear-gradient(45deg, #7ed9b2, var(--primary-color)); /* Измененный градиент при наведении */
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(168, 230, 207, 0.6);
}
</style>
 