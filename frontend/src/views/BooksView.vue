<template>
  <div class="books-page">
    <div class="container mt-4 pb-5">
      <!-- Заголовок -->
      <h1 class="section-title text-center">Библиотека книг</h1>

      <!-- Фильтры и поиск -->
      <section class="filters-section mb-5">
        <div class="filters-panel">
          <div class="row g-3">
            <!-- Поиск -->
            <div class="col-12 col-md-4">
              <div class="search-box">
                <i class="bi bi-search"></i>
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Поиск по названию или автору..."
                  v-model="searchQuery"
                >
              </div>
            </div>
            
            <!-- Выпадающие списки -->
            <div class="col-12 col-md-8">
              <div class="row g-3">
                <div class="col-6 col-md-3">
                  <select class="form-select" v-model="filters.genre">
                    <option value="">Жанр</option>
                    <option v-for="genre in genres" :key="genre" :value="genre">
                      {{ genre }}
                    </option>
                  </select>
                </div>
                <div class="col-6 col-md-3">
                  <select class="form-select" v-model="filters.ageCategory">
                    <option value="">Возраст</option>
                    <option v-for="age in ageCategories" :key="age" :value="age">
                      {{ age }}
                    </option>
                  </select>
                </div>
                <div class="col-6 col-md-3">
                  <select class="form-select" v-model="filters.rating">
                    <option value="">Рейтинг</option>
                    <option v-for="rating in ratingOptions" :key="rating.value" :value="rating.value">
                      {{ rating.label }}
                    </option>
                  </select>
                </div>
                <div class="col-6 col-md-3">
                  <select class="form-select" v-model="filters.sortBy">
                    <option value="">Сортировка</option>
                    <option v-for="sort in sortOptions" :key="sort.value" :value="sort.value">
                      {{ sort.label }}
                    </option>
                  </select>
                </div>

              </div>
            </div>
          </div>
        </div>
      </section>



      <!-- Основной список книг -->
      <section class="books-section mb-5">
        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
          <div class="col" v-for="book in filteredBooks" :key="book.id">
            <div class="book-card" :class="{ 'premium': book.isPremium }">
              <div class="premium-badge" v-if="book.isPremium">
                <i class="bi bi-crown"></i>
                <span>Премиум</span>
              </div>
              <div class="book-cover">
                <img :src="book.cover" :alt="book.title" @error="handleImageError">
              </div>
              <div class="book-info">
                <h3 class="book-title">{{ book.title }}</h3>
                <p class="book-author">{{ book.author?.name || 'Автор не указан' }}</p>
                <div class="book-rating">
                  <i class="bi bi-star-fill" v-for="n in 5" :key="n" 
                     :class="{ 'active': n <= Math.round(book.rating || 0) }"></i>
                  <span>{{ typeof book.rating === 'number' ? book.rating.toFixed(1) : '0.0' }}</span>
                </div>
                <div class="book-votes" v-if="book.vote_count !== undefined">
                  <i class="bi bi-hand-thumbs-up"></i>
                  <span>{{ book.vote_count }} голосов</span>
                </div>
                <div class="book-meta">
                  <span class="book-genre">{{ book.genre }}</span>
                  <span class="book-age">{{ book.ageCategory }}</span>
                </div>
                <div class="book-actions">
                  <RouterLink :to="`/books/${book.id}`" class="btn book-action-button">К книге</RouterLink>
                  <button class="btn btn-outline-primary" @click="rateBook(book)">
                    Оценить
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Пагинация -->
        <div class="pagination-section text-center mt-4">
          <button class="btn btn-outline-primary me-2" 
                  :disabled="currentPage === 1"
                  @click="goToPreviousPage">
            Назад
          </button>
          <span class="page-info">Страница {{ currentPage }} из {{ totalPages }}</span>
          <button class="btn btn-outline-primary ms-2" 
                  :disabled="currentPage === totalPages"
                  @click="goToNextPage">
            Вперед
          </button>
        </div>
      </section>

      <!-- Рекомендации -->
      <section class="recommendations-section" v-if="recommendedBooks.length">
        <h2 class="section-subtitle">Тебе понравится</h2>
        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-5 g-4">
          <div class="col" v-for="book in recommendedBooks" :key="book.id">
            <div class="book-card recommended">
              <div class="book-cover">
                <img :src="book.cover" :alt="book.title" @error="handleImageError">
              </div>
              <div class="book-info">
                <h3 class="book-title">{{ book.title }}</h3>
                <p class="book-author">{{ book.author?.name || 'Автор не указан' }}</p>
                <div class="book-rating">
                  <i class="bi bi-star-fill" v-for="n in 5" :key="n" 
                     :class="{ 'active': n <= Math.round(book.rating || 0) }"></i>
                  <span>{{ typeof book.rating === 'number' ? book.rating.toFixed(1) : '0.0' }}</span>
                </div>
                <div class="book-meta">
                  <span class="book-genre">{{ book.genre }}</span>
                </div>
                <button class="btn book-action-button w-100">К книге</button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Модальное окно оценки -->
    <div class="rating-modal" v-if="showRatingModal" @click.self="closeRatingModal">
      <div class="modal-content">
        <button class="btn-close" @click="closeRatingModal"></button>
        <h3>Оцените книгу</h3>
        <div class="rating-stars">
          <i class="bi bi-star" 
             v-for="n in 5" 
             :key="n"
             :class="{ 'bi-star-fill': n <= selectedRating }"
             @click="selectRating(n)"
             @mouseover="hoverRating = n"
             @mouseleave="hoverRating = 0"></i>
        </div>
        <button class="btn btn-primary mt-3" @click="submitRating">
          Оценить
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { getBooks, getTopBooks, getRecommendedBooks, rateBook as rateBookApi, getGenres, getAgeCategories } from '@/api/books';
import type { Book } from '@/types/book';

const route = useRoute();

// Состояние фильтров
const searchQuery = ref('');
const filters = ref({
  genre: '',
  ageCategory: '',
  rating: '',
  sortBy: ''
});

// Состояние пагинации
const currentPage = ref(1);
const booksPerPage = 12;
const totalBooks = ref(0);

// Состояние загрузки и ошибок
const isLoading = ref(false);
const error = ref<string | null>(null);

// Состояние книг
const books = ref<Book[]>([]);
const topBooks = ref<Book[]>([]);
const recommendedBooks = ref<Book[]>([]);

// Состояние модального окна оценки
const showRatingModal = ref(false);
const selectedBook = ref<Book | null>(null);
const selectedRating = ref(0);
const hoverRating = ref(0);

// Данные для фильтров
const genres = ref<string[]>([]);
const ageCategories = ref<string[]>([]);
const ratingOptions = [
  { value: '4', label: 'От 4.0 и выше' },
  { value: '3', label: 'От 3.0 и выше' },
  { value: '2', label: 'От 2.0 и выше' }
];
const sortOptions = [
  { value: 'rating', label: 'По рейтингу' },
  { value: 'newest', label: 'По новизне' },
  { value: 'alphabet', label: 'По алфавиту' }
];

// Загрузка данных
const loadBooks = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await getBooks({
      page: currentPage.value,
      limit: booksPerPage,
      search: searchQuery.value,
      genre: filters.value.genre,
      ageCategory: filters.value.ageCategory,
      rating: filters.value.rating ? Number(filters.value.rating) : undefined,
      sortBy: filters.value.sortBy
    });
    books.value = response.books;
    totalBooks.value = response.total;
  } catch (e) {
    error.value = 'Ошибка при загрузке книг';
    console.error(e);
  } finally {
    isLoading.value = false;
  }
};

const loadTopBooks = async () => {
  try {
    topBooks.value = await getTopBooks();
  } catch (e) {
    console.error('Ошибка при загрузке топ книг:', e);
  }
};

const loadRecommendedBooks = async () => {
  try {
    recommendedBooks.value = await getRecommendedBooks();
  } catch (e) {
    console.error('Ошибка при загрузке рекомендуемых книг:', e);
  }
};

const loadGenres = async () => {
  try {
    genres.value = await getGenres();
  } catch (e) {
    console.error('Ошибка при загрузке жанров:', e);
  }
};

const loadAgeCategories = async () => {
  try {
    ageCategories.value = await getAgeCategories();
  } catch (e) {
    console.error('Ошибка при загрузке возрастных категорий:', e);
  }
};

// Вычисляемые свойства
const totalPages = computed(() => Math.ceil(totalBooks.value / booksPerPage));
const filteredBooks = computed(() => books.value);

// Методы
const rateBook = (book: Book) => {
  selectedBook.value = book;
  selectedRating.value = 0;
  showRatingModal.value = true;
};

const selectRating = (rating: number) => {
  selectedRating.value = rating;
};

const submitRating = async () => {
  if (!selectedBook.value || !selectedRating.value) return;
  
  try {
    await rateBookApi(selectedBook.value.id, selectedRating.value);
    // Обновляем рейтинг книги в списке
    const book = books.value.find((b: Book) => b.id === selectedBook.value?.id);
    if (book) {
      book.rating = selectedRating.value;
    }
    closeRatingModal();
  } catch (e) {
    console.error('Ошибка при оценке книги:', e);
  }
};

const closeRatingModal = () => {
  showRatingModal.value = false;
  selectedBook.value = null;
  selectedRating.value = 0;
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



// Загрузка данных при монтировании компонента
onMounted(async () => {
  // Читаем параметр поиска из URL
  if (route.query.search && typeof route.query.search === 'string') {
    searchQuery.value = route.query.search;
  }
  
  await Promise.all([
    loadBooks(),
    loadTopBooks(),
    loadRecommendedBooks(),
    loadGenres(),
    loadAgeCategories()
  ]);
});

// Функции пагинации с прокруткой
const scrollToTop = () => {
  const booksSection = document.querySelector('.books-section');
  if (booksSection) {
    booksSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } else {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const goToPreviousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    scrollToTop();
  }
};

const goToNextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    scrollToTop();
  }
};

// Следим за изменениями фильтров и поиска
watch([searchQuery, filters], () => {
  currentPage.value = 1; // Сбрасываем на первую страницу при изменении фильтров
  loadBooks();
}, { deep: true });

// Отдельно следим за изменением страницы
watch(currentPage, () => {
  loadBooks();
});
</script>

<style scoped>
.books-page {
  min-height: calc(100vh - var(--header-height, 60px) - var(--footer-height, 60px));
  padding-top: var(--header-height, 60px);
  color: #fff;
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
}

.section-title {
  color: #a8e6cf;
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 2.5rem;
  position: relative;
}

.section-subtitle {
  color: #a8e6cf;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 2rem;
}

/* Фильтры */
.filters-panel {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 15px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.search-box {
  position: relative;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #a8e6cf;
}

.search-box input {
  padding-left: 2.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(168, 230, 207, 0.2);
  color: #fff !important;
}

.search-box input::placeholder {
  color: rgba(255, 255, 255, 0.6) !important;
}

.search-box input:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: #a8e6cf;
  box-shadow: 0 0 0 0.25rem rgba(168, 230, 207, 0.25);
  color: #fff !important;
}

.form-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(168, 230, 207, 0.2);
  color: #fff;
}

.form-select:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: #a8e6cf;
  box-shadow: 0 0 0 0.25rem rgba(168, 230, 207, 0.25);
}

/* Карточки книг */
.book-card {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  backdrop-filter: blur(20px);
  border: 1px solid rgba(168, 230, 207, 0.2);
  border-radius: 12px;
  padding: 0.75rem;
  height: 100%;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.book-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(168, 230, 207, 0.1) 0%, rgba(140, 211, 176, 0.05) 50%, rgba(168, 230, 207, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
  border-radius: 20px;
}

.book-card:hover {
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3), 0 5px 15px rgba(168, 230, 207, 0.2);
  border-color: rgba(168, 230, 207, 0.4);
}

.book-card:hover::before {
  opacity: 1;
}

.book-card.premium {
  background: linear-gradient(145deg, rgba(255, 215, 0, 0.15), rgba(255, 165, 0, 0.1));
  border-color: rgba(255, 215, 0, 0.3);
  box-shadow: 0 4px 20px rgba(255, 215, 0, 0.1);
}

.book-card.premium:hover {
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3), 0 5px 15px rgba(255, 215, 0, 0.3);
  border-color: rgba(255, 215, 0, 0.5);
}

.book-cover {
  position: relative;
  padding-top: 140%;
  margin-bottom: 0.75rem;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.book-cover::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(168, 230, 207, 0.1) 0%, transparent 50%, rgba(168, 230, 207, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  z-index: 1;
}

.book-card:hover .book-cover {
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
}

.book-card:hover .book-cover::after {
  opacity: 1;
}

.book-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}



.book-info {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  gap: 0.5rem;
}

.book-title {
  font-size: 1rem;
  font-weight: bold;
  color: #a8e6cf;
  margin-bottom: 0.25rem;
  line-height: 1.2;
  height: 2.4rem;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  text-overflow: ellipsis;
}

.book-author {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 0.25rem;
  line-height: 1.1;
  height: 1.1rem;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.book-rating {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  height: 1.5rem;
  flex-shrink: 0;
}

.book-rating i {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.9rem;
}

.book-rating i.active {
  color: #ffd700;
}

.book-rating span {
  margin-left: 0.5rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
  font-weight: 500;
}

.book-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: flex-start;
}

.book-genre, .book-age {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
    max-width: 100%;
  }
  
  .book-actions {
    display: flex;
    gap: 0.4rem;
    margin-top: auto;
    padding-top: 0.5rem;
  }

.book-actions .btn {
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  z-index: 2;
}

.book-actions .btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.book-actions .btn:hover::before {
  left: 100%;
}

.book-actions .btn-primary {
  background: linear-gradient(135deg, #a8e6cf 0%, #8cd3b0 100%);
  border: none;
  color: #1a1a1a;
  box-shadow: 0 4px 15px rgba(168, 230, 207, 0.3);
}

.book-actions .btn-primary:hover {
  box-shadow: 0 8px 25px rgba(168, 230, 207, 0.4);
  background: linear-gradient(135deg, #8cd3b0 0%, #a8e6cf 100%);
}

.book-actions .btn-outline-primary {
  background: transparent;
  border: 2px solid rgba(168, 230, 207, 0.5);
  color: #a8e6cf;
}

.book-actions .btn-outline-primary:hover {
  background: rgba(168, 230, 207, 0.1);
  border-color: #a8e6cf;
  box-shadow: 0 6px 20px rgba(168, 230, 207, 0.2);
}

/* Топ книги */
.book-card.top-book {
  background: linear-gradient(145deg, rgba(255, 215, 0, 0.2), rgba(255, 165, 0, 0.15));
  border: 2px solid rgba(255, 215, 0, 0.4);
  box-shadow: 0 6px 30px rgba(255, 215, 0, 0.2);
  position: relative;
}

.book-card.top-book::before {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.15) 0%, rgba(255, 165, 0, 0.1) 50%, rgba(255, 215, 0, 0.15) 100%);
}

.book-card.top-book:hover {
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3), 0 8px 25px rgba(255, 215, 0, 0.4);
  border-color: rgba(255, 215, 0, 0.6);
}

.book-card.top-book .book-info {
  padding-bottom: 1rem;
}

.book-card.top-book .book-title {
  color: #ffd700;
  text-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
  font-weight: 700;
}

.book-card.top-book .book-cover {
  box-shadow: 0 10px 30px rgba(255, 215, 0, 0.2);
}

.book-card.top-book:hover .book-cover {
  box-shadow: 0 15px 40px rgba(255, 215, 0, 0.3);
}

/* Бейджи */
.premium-badge, .popular-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: linear-gradient(45deg, #ffd700, #ffa500);
  color: #1a1a1a;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  z-index: 1;
}

.premium-badge i, .popular-badge i {
  color: #1a1a1a;
}

/* Модальное окно оценки */
.rating-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #2c3e50;
  border-radius: 15px;
  padding: 2rem;
  text-align: center;
  position: relative;
  max-width: 400px;
  width: 90%;
}

.rating-stars {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  font-size: 2rem;
  margin: 1rem 0;
}

.rating-stars i {
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: color 0.2s ease;
}

.rating-stars i:hover {
  color: #ffd700;
}

.rating-stars i.bi-star-fill {
  color: #ffd700;
}

.rating-modal .btn-primary:hover {
  background-color: var(--primary-dark-color);
  border-color: var(--primary-dark-color);
}

.book-action-button {
  background-color: #a8e6cf;
  color: #1a1a1a;
  border: none;
  border-radius: 8px;
  padding: 10px 15px;
  font-size: 1rem;
  font-weight: 600;
  transition: background-color 0.3s ease, transform 0.2s ease;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.book-action-button:hover {
  background-color: #8cd3b0;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
}

.book-action-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* Пагинация */
.pagination-section {
  margin-top: 3rem;
  padding: 2rem 0;
}

.pagination-section .btn {
  border-radius: 12px;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.pagination-section .btn-outline-primary {
  background: rgba(168, 230, 207, 0.1);
  border: 2px solid rgba(168, 230, 207, 0.3);
  color: #a8e6cf;
}

.pagination-section .btn-outline-primary:not(:disabled):hover {
  background: rgba(168, 230, 207, 0.2);
  border-color: #a8e6cf;
  box-shadow: 0 8px 25px rgba(168, 230, 207, 0.3);
}

.pagination-section .btn:disabled {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.3);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.page-info {
  color: rgba(255, 255, 255, 0.8);
  margin: 0 1.5rem;
  font-weight: 500;
  font-size: 1.1rem;
  background: rgba(168, 230, 207, 0.1);
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  border: 1px solid rgba(168, 230, 207, 0.2);
}

/* Стили для голосования */
.book-votes {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #a8e6cf;
  font-size: 0.9rem;
}

.book-votes i {
  font-size: 1rem;
}

.book-votes span {
  color: rgba(255, 255, 255, 0.8);
}

/* Адаптивность */
@media (max-width: 768px) {
  .section-title {
    font-size: 2rem;
  }

  .section-subtitle {
    font-size: 1.5rem;
  }

  .filters-panel {
    padding: 1rem;
  }

  .book-card {
    padding: 0.75rem;
  }

  .book-title {
    font-size: 1rem;
    height: 2.4rem;
  }

  .book-author {
    font-size: 0.8rem;
  }

  .book-rating {
    margin-bottom: 0.75rem;
  }

  .book-rating i {
    font-size: 0.8rem;
  }

  .book-meta {
    margin-bottom: 0.75rem;
  }

  .book-genre, .book-age {
    font-size: 0.7rem;
    padding: 0.15rem 0.3rem;
  }

  .book-actions {
    flex-direction: column;
    gap: 0.4rem;
  }

  .book-actions .btn {
    width: 100%;
    font-size: 0.9rem;
    padding: 0.5rem;
  }

  .premium-badge, .popular-badge {
    top: 0.5rem;
    right: 0.5rem;
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
  }
}
</style>