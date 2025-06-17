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

      <!-- Топ недели -->
      <section class="top-books-section mb-5" v-if="topBooks.length">
        <h2 class="section-subtitle">Топ недели</h2>
        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-5 g-4">
          <div class="col" v-for="book in topBooks" :key="book.id">
            <div class="book-card top-book">
              <div class="popular-badge">
                <i class="bi bi-fire"></i>
                <span>Популярно</span>
              </div>
              <div class="book-cover">
                <img :src="book.cover" :alt="book.title">
              </div>
              <div class="book-info">
                <h3 class="book-title">{{ book.title }}</h3>
                <p class="book-author">{{ book.author }}</p>
                <div class="book-rating">
                  <i class="bi bi-star-fill" v-for="n in 5" :key="n" 
                     :class="{ 'active': n <= Math.round(book.rating) }"></i>
                  <span>{{ book.rating.toFixed(1) }}</span>
                </div>
                <div class="book-meta">
                  <span class="book-genre">{{ book.genre }}</span>
                  <span class="book-age">{{ book.ageCategory }}</span>
                </div>
                <button class="btn btn-primary w-100">К книге</button>
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
                <img :src="book.cover" :alt="book.title">
              </div>
              <div class="book-info">
                <h3 class="book-title">{{ book.title }}</h3>
                <p class="book-author">{{ book.author }}</p>
                <div class="book-rating">
                  <i class="bi bi-star-fill" v-for="n in 5" :key="n" 
                     :class="{ 'active': n <= Math.round(book.rating) }"></i>
                  <span>{{ book.rating.toFixed(1) }}</span>
                </div>
                <div class="book-meta">
                  <span class="book-genre">{{ book.genre }}</span>
                  <span class="book-age">{{ book.ageCategory }}</span>
                </div>
                <div class="book-actions">
                  <button class="btn btn-outline-primary" @click="rateBook(book)">
                    Оценить
                  </button>
                  <button class="btn btn-primary">К книге</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Пагинация -->
        <div class="pagination-section text-center mt-4">
          <button class="btn btn-outline-primary me-2" 
                  :disabled="currentPage === 1"
                  @click="currentPage--">
            Назад
          </button>
          <span class="page-info">Страница {{ currentPage }} из {{ totalPages }}</span>
          <button class="btn btn-outline-primary ms-2" 
                  :disabled="currentPage === totalPages"
                  @click="currentPage++">
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
                <img :src="book.cover" :alt="book.title">
              </div>
              <div class="book-info">
                <h3 class="book-title">{{ book.title }}</h3>
                <p class="book-author">{{ book.author }}</p>
                <div class="book-rating">
                  <i class="bi bi-star-fill" v-for="n in 5" :key="n" 
                     :class="{ 'active': n <= Math.round(book.rating) }"></i>
                  <span>{{ book.rating.toFixed(1) }}</span>
                </div>
                <div class="book-meta">
                  <span class="book-genre">{{ book.genre }}</span>
                </div>
                <button class="btn btn-primary w-100">К книге</button>
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
import { booksApi, type Book } from '@/api/books';

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
    const response = await booksApi.getBooks({
      page: currentPage.value,
      perPage: booksPerPage,
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
    topBooks.value = await booksApi.getTopBooks();
  } catch (e) {
    console.error('Ошибка при загрузке топ книг:', e);
  }
};

const loadRecommendedBooks = async () => {
  try {
    recommendedBooks.value = await booksApi.getRecommendedBooks();
  } catch (e) {
    console.error('Ошибка при загрузке рекомендуемых книг:', e);
  }
};

// Вычисляемые свойства
const totalPages = computed(() => Math.ceil(totalBooks.value / booksPerPage));

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
    await booksApi.rateBook(selectedBook.value.id, selectedRating.value);
    // Обновляем рейтинг книги в списке
    const book = books.value.find(b => b.id === selectedBook.value?.id);
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

// Загрузка данных при монтировании компонента
onMounted(async () => {
  await Promise.all([
    loadBooks(),
    loadTopBooks(),
    loadRecommendedBooks()
  ]);
});

// Следим за изменениями фильтров и поиска
watch([searchQuery, filters, currentPage], () => {
  loadBooks();
}, { deep: true });
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
  color: #fff;
}

.search-box input:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: #a8e6cf;
  box-shadow: 0 0 0 0.25rem rgba(168, 230, 207, 0.25);
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
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 15px;
  padding: 1rem;
  height: 100%;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
  overflow: hidden;
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
}

.book-card.premium {
  background: linear-gradient(45deg, rgba(168, 230, 207, 0.1), rgba(140, 211, 176, 0.1));
  border-color: rgba(168, 230, 207, 0.3);
}

.book-cover {
  position: relative;
  padding-top: 140%;
  margin-bottom: 1rem;
  border-radius: 10px;
  overflow: hidden;
}

.book-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-info {
  padding: 0.5rem;
}

.book-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #a8e6cf;
  margin-bottom: 0.5rem;
}

.book-author {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 0.5rem;
}

.book-rating {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.book-rating i {
  color: rgba(255, 255, 255, 0.3);
}

.book-rating i.active {
  color: #ffd700;
}

.book-rating span {
  margin-left: 0.5rem;
  color: rgba(255, 255, 255, 0.7);
}

.book-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.book-genre, .book-age {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.book-actions {
  display: flex;
  gap: 0.5rem;
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

/* Пагинация */
.pagination-section {
  margin-top: 2rem;
}

.page-info {
  color: rgba(255, 255, 255, 0.7);
  margin: 0 1rem;
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
    font-size: 1.1rem;
  }

  .book-author {
    font-size: 0.8rem;
  }

  .book-actions {
    flex-direction: column;
  }

  .book-actions .btn {
    width: 100%;
  }
}
</style> 