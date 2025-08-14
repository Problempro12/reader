<template>
  <div class="book-detail-page">
    <div class="container mt-4 pb-5">
      <!-- Загрузка -->
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="mt-3">Загрузка информации о книге...</p>
      </div>

      <!-- Ошибка -->
      <div v-else-if="error" class="alert alert-danger text-center">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
        <div class="mt-3">
          <RouterLink to="/books" class="btn btn-outline-light">
            <i class="bi bi-arrow-left me-2"></i>
            Вернуться к каталогу
          </RouterLink>
        </div>
      </div>

      <!-- Детали книги -->
      <div v-else-if="book" class="book-detail-content">
        <!-- Навигация -->
        <nav class="breadcrumb-nav mb-4">
          <RouterLink to="/books" class="breadcrumb-link">
            <i class="bi bi-arrow-left me-2"></i>
            Каталог книг
          </RouterLink>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">{{ book.title }}</span>
        </nav>

        <!-- Основная информация -->
        <div class="row g-4 mb-5">
          <!-- Обложка -->
          <div class="col-lg-4">
            <div class="book-cover-section">
              <div class="book-cover-large">
                <img :src="book.cover" :alt="book.title" @error="handleImageError">
                <div class="premium-overlay" v-if="book.isPremium">
                  <i class="bi bi-crown"></i>
                  <span>Премиум</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Информация -->
          <div class="col-lg-8">
            <div class="book-info-section">
              <h1 class="book-title">{{ book.title }}</h1>
              <p class="book-author">{{ book.author?.name || 'Автор не указан' }}</p>
              
              <!-- Рейтинг -->
              <div class="book-rating-section mb-4">
                <div class="rating-display">
                  <div class="rating-stars">
                    <i v-for="n in 5" :key="n" :class="[
                  'bi rating-star',
                  n <= Math.round(userRating || book.rating || 0) ? 'bi-star-fill active' : 'bi-star inactive'
                ]"></i>
                  </div>
                  <div class="rating-info">
                    <div class="rating-main">
                      <span class="rating-value">{{ typeof book.rating === 'number' ? book.rating.toFixed(1) : '0.0' }}</span>
                      <div class="rating-details" v-if="book.ratingCount">
                        <span>{{ book.ratingCount }} оценок</span>
                        <span v-if="book.reviewsCount"> • {{ book.reviewsCount }} отзывов</span>
                      </div>
                    </div>
                    <div v-if="userRating" class="user-rating-badge">
                      <small class="text-muted">Ваша: {{ userRating }}★</small>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Метаданные -->
              <div class="book-meta-section mb-4">
                <div class="meta-item">
                  <span class="meta-label">Жанр:</span>
                  <span class="meta-value">{{ book.genre }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">Возрастная категория:</span>
                  <span class="meta-value">{{ book.ageCategory }}</span>
                </div>
                <div class="meta-item" v-if="book.series">
                  <span class="meta-label">Серия:</span>
                  <span class="meta-value">{{ book.series }}</span>
                </div>
                <div class="meta-item" v-if="book.translator">
                  <span class="meta-label">Переводчик:</span>
                  <span class="meta-value">{{ book.translator }}</span>
                </div>
              </div>

              <!-- Цена -->
              <div class="price-section mb-4" v-if="book.price">
                <div class="price-current">{{ book.price.current }}</div>
                <div class="price-details">
                  <span class="price-discount" v-if="book.price.discount">{{ book.price.discount }}</span>
                  <span class="price-subscriber" v-if="book.price.subscriber">Для подписчиков: {{ book.price.subscriber }}</span>
                </div>
              </div>

              <!-- Голосование -->
              <div class="book-voting-section mb-4" v-if="voteInfo">
                <div class="vote-display">
                  <div class="vote-count">
                    <i class="bi bi-hand-thumbs-up me-2"></i>
                    <span class="vote-number">{{ voteInfo.vote_count }}</span>
                    <span class="vote-text">голосов</span>
                  </div>
                  <button 
                    class="btn btn-vote" 
                    :class="voteInfo.user_voted ? 'btn-success' : 'btn-outline-primary'"
                    @click="toggleVote"
                    :disabled="isVoting">
                    <i class="bi" :class="voteInfo.user_voted ? 'bi-hand-thumbs-up-fill' : 'bi-hand-thumbs-up'"></i>
                    {{ voteInfo.user_voted ? 'Голос отдан' : 'Отдать голос' }}
                  </button>
                </div>
              </div>

              <!-- Действия -->
              <div class="book-actions">
                <RouterLink :to="`/books/${book.id}/read`" class="btn btn-primary btn-lg">
                  <i class="bi bi-book-open me-2"></i>
                  Читать книгу
                </RouterLink>
                
                <!-- Система списков -->
                <div class="list-actions">
                  <div v-if="!userBookStatus" class="dropdown">
                    <button class="btn btn-outline-primary btn-lg dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                      <i class="bi bi-bookmark-plus me-2"></i>
                      В список
                    </button>
                    <ul class="dropdown-menu">
                      <li><a class="dropdown-item" href="#" @click.prevent="addToList('planned')">
                        <i class="bi bi-calendar-plus me-2"></i>В планах
                      </a></li>
                      <li><a class="dropdown-item" href="#" @click.prevent="addToList('reading')">
                        <i class="bi bi-book me-2"></i>Читаю
                      </a></li>
                      <li><a class="dropdown-item" href="#" @click.prevent="addToList('completed')">
                        <i class="bi bi-check-circle me-2"></i>Прочитано
                      </a></li>
                      <li><a class="dropdown-item" href="#" @click.prevent="addToList('dropped')">
                        <i class="bi bi-x-circle me-2"></i>Брошено
                      </a></li>
                    </ul>
                  </div>
                  
                  <div v-else class="list-status-actions">
                    <div class="dropdown">
                      <button class="btn btn-success btn-lg dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="bi" :class="getStatusIcon(userBookStatus)"></i>
                        {{ getStatusText(userBookStatus) }}
                      </button>
                      <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#" @click.prevent="updateStatus('planned')" :class="{ active: userBookStatus === 'planned' }">
                          <i class="bi bi-calendar-plus me-2"></i>В планах
                        </a></li>
                        <li><a class="dropdown-item" href="#" @click.prevent="updateStatus('reading')" :class="{ active: userBookStatus === 'reading' }">
                          <i class="bi bi-book me-2"></i>Читаю
                        </a></li>
                        <li><a class="dropdown-item" href="#" @click.prevent="updateStatus('completed')" :class="{ active: userBookStatus === 'completed' }">
                          <i class="bi bi-check-circle me-2"></i>Прочитано
                        </a></li>
                        <li><a class="dropdown-item" href="#" @click.prevent="updateStatus('dropped')" :class="{ active: userBookStatus === 'dropped' }">
                          <i class="bi bi-x-circle me-2"></i>Брошено
                        </a></li>
                      </ul>
                    </div>
                    <button class="btn btn-outline-danger btn-lg" @click="removeFromList">
                      <i class="bi bi-trash me-2"></i>
                      Удалить из списка
                    </button>
                  </div>
                </div>
                
                <button class="btn btn-outline-secondary btn-lg" @click="rateBook">
                  <i class="bi bi-star me-2"></i>
                  Оценить
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Описание -->
        <div class="book-description-section mb-5">
          <h2 class="section-title">Описание</h2>
          <div class="description-content">
            <p>{{ book.description }}</p>
          </div>
        </div>

        <!-- Техническая информация -->
        <div class="technical-info-section" v-if="book.technical">
          <h2 class="section-title">Техническая информация</h2>
          <div class="row g-3">
            <div class="col-md-6" v-if="book.technical.volume">
              <div class="tech-item">
                <span class="tech-label">Объем:</span>
                <span class="tech-value">{{ book.technical.volume }}</span>
              </div>
            </div>
            <div class="col-md-6" v-if="book.technical.year">
              <div class="tech-item">
                <span class="tech-label">Год издания:</span>
                <span class="tech-value">{{ book.technical.year }}</span>
              </div>
            </div>
            <div class="col-md-6" v-if="book.technical.isbn">
              <div class="tech-item">
                <span class="tech-label">ISBN:</span>
                <span class="tech-value">{{ book.technical.isbn }}</span>
              </div>
            </div>
            <div class="col-md-6" v-if="book.technical.copyrightHolder">
              <div class="tech-item">
                <span class="tech-label">Правообладатель:</span>
                <span class="tech-value">{{ book.technical.copyrightHolder }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bootstrap Модальное окно оценки -->
    <div class="modal fade" id="ratingModal" tabindex="-1" aria-labelledby="ratingModalLabel" aria-hidden="true" v-if="showRatingModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content rating-modal">
          <div class="modal-header">
            <h5 class="modal-title" id="ratingModalLabel">
              <i class="bi bi-star-fill me-2 text-warning"></i>
              Оценить книгу
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="closeRatingModal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="text-center">
              <div class="book-title-modal mb-4">
                <i class="bi bi-book me-2"></i>
                {{ book?.title }}
              </div>
              <div class="rating-stars-modal mb-4">
                <i v-for="n in 5" 
                   :key="n"
                   :class="[
                     'bi rating-star-interactive',
                     n <= (hoverRating || selectedRating) ? 'bi-star-fill active' : 'bi-star inactive'
                   ]"
                   @click="selectRating(n)"
                   @mouseenter="hoverRating = n"
                   @mouseleave="hoverRating = 0"></i>
              </div>
              <div class="rating-text">
                <span v-if="selectedRating || hoverRating" class="rating-description">
                  {{ getRatingText(hoverRating || selectedRating) }}
                </span>
                <span v-else class="rating-hint">
                  <i class="bi bi-hand-index me-1"></i>
                  Нажмите на звезду для оценки
                </span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-light" @click="closeRatingModal">
              <i class="bi bi-x-circle me-2"></i>
              Отмена
            </button>
            <button type="button" class="btn btn-gradient" @click="submitRating" :disabled="!selectedRating">
              <i class="bi bi-check-circle me-2"></i>
              Оценить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { useRoute, useRouter, RouterLink } from 'vue-router';
import { getBook, rateBook as rateBookApi, getBookRating, getBookVoteInfo, voteForBook, removeVoteForBook, getUserBooks, addUserBook, updateUserBookStatus, removeUserBook } from '@/api/books';
import type { Book } from '@/types/book';

// Bootstrap Modal
declare global {
  interface Window {
    bootstrap: any;
  }
}

const route = useRoute();
const router = useRouter();

// Состояние
const book = ref<Book | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);
const showRatingModal = ref(false);
const selectedRating = ref(0);
const hoverRating = ref(0);
const userRating = ref<number | null>(null);
const voteInfo = ref<{vote_count: number, user_voted: boolean} | null>(null);
const isVoting = ref(false);
const userBookStatus = ref<string | null>(null);
const userBookId = ref<number | null>(null);
const isUpdatingStatus = ref(false);
let modalInstance: any = null;

// Загрузка книги
const loadBook = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    const bookId = Number(route.params.id);
    
    if (isNaN(bookId)) {
      throw new Error('Некорректный ID книги');
    }
    
    // Загружаем данные книги, рейтинг, информацию о голосах и статус в библиотеке параллельно
    const [bookData, ratingData, voteData, userBooksData] = await Promise.all([
      getBook(bookId),
      getBookRating(bookId).catch(() => ({ user_rating: null, average_rating: 0, rating_count: 0 })),
      getBookVoteInfo(bookId).catch(() => ({ vote_count: 0, user_voted: false })),
      getUserBooks().catch(() => [])
    ]);
    
    book.value = bookData;
    userRating.value = ratingData.user_rating;
    voteInfo.value = voteData;
    
    // Проверяем, есть ли книга в библиотеке пользователя
    const userBook = userBooksData.find((ub: any) => ub.book.id === bookId);
    if (userBook) {
      userBookStatus.value = userBook.status;
      userBookId.value = userBook.id;
    }
    
    // Обновляем рейтинг книги из API рейтинга
    if (book.value) {
      book.value.rating = ratingData.average_rating;
      book.value.ratingCount = ratingData.rating_count;
    }
  } catch (e: any) {
    console.error('Ошибка при загрузке книги:', e);
    error.value = e.response?.status === 404 
      ? 'Книга не найдена' 
      : 'Ошибка при загрузке книги';
  } finally {
    isLoading.value = false;
  }
};

// Обработка ошибки изображения
const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement;
  target.src = '/placeholder-book.svg';
};

// Действия со списками
const addToList = async (status: string) => {
  if (!book.value || isUpdatingStatus.value) return;
  
  try {
    isUpdatingStatus.value = true;
    const response = await addUserBook(book.value.id, status);
    userBookStatus.value = status;
    userBookId.value = response.id;
    
    // Показываем уведомление об успехе
    const statusText = getStatusText(status);
    console.log(`Книга добавлена в список: ${statusText}`);
  } catch (error: any) {
    console.error('Ошибка при добавлении в список:', error);
    
    // Показываем пользователю понятное сообщение об ошибке
    if (error.response?.status === 401) {
      alert('Для добавления книг в список необходимо войти в систему');
    } else if (error.response?.status === 400) {
      alert('Книга уже добавлена в ваш список');
    } else {
      alert('Произошла ошибка при добавлении книги в список. Попробуйте еще раз.');
    }
  } finally {
    isUpdatingStatus.value = false;
  }
};

const updateStatus = async (newStatus: string) => {
  if (!userBookId.value || isUpdatingStatus.value || userBookStatus.value === newStatus) return;
  
  try {
    isUpdatingStatus.value = true;
    await updateUserBookStatus(userBookId.value, newStatus);
    userBookStatus.value = newStatus;
    
    // Показываем уведомление об успехе
    const statusText = getStatusText(newStatus);
    console.log(`Статус книги изменен на: ${statusText}`);
  } catch (error: any) {
    console.error('Ошибка при обновлении статуса:', error);
    
    // Показываем пользователю понятное сообщение об ошибке
    if (error.response?.status === 401) {
      alert('Для изменения статуса книги необходимо войти в систему');
    } else {
      alert('Произошла ошибка при изменении статуса книги. Попробуйте еще раз.');
    }
  } finally {
    isUpdatingStatus.value = false;
  }
};

const removeFromList = async () => {
  if (!userBookId.value || isUpdatingStatus.value) return;
  
  try {
    isUpdatingStatus.value = true;
    await removeUserBook(userBookId.value);
    userBookStatus.value = null;
    userBookId.value = null;
    
    console.log('Книга удалена из списка');
  } catch (error: any) {
    console.error('Ошибка при удалении из списка:', error);
    
    // Показываем пользователю понятное сообщение об ошибке
    if (error.response?.status === 401) {
      alert('Для удаления книги из списка необходимо войти в систему');
    } else {
      alert('Произошла ошибка при удалении книги из списка. Попробуйте еще раз.');
    }
  } finally {
    isUpdatingStatus.value = false;
  }
};

// Вспомогательные функции для отображения
const getStatusText = (status: string): string => {
  const statusTexts: Record<string, string> = {
    'planned': 'В планах',
    'reading': 'Читаю',
    'completed': 'Прочитано',
    'dropped': 'Брошено'
  };
  return statusTexts[status] || status;
};

const getStatusIcon = (status: string): string => {
  const statusIcons: Record<string, string> = {
    'planned': 'bi-calendar-plus me-2',
    'reading': 'bi-book me-2',
    'completed': 'bi-check-circle me-2',
    'dropped': 'bi-x-circle me-2'
  };
  return statusIcons[status] || 'bi-bookmark me-2';
};

const rateBook = async () => {
  selectedRating.value = 0;
  hoverRating.value = 0;
  showRatingModal.value = true;
  
  await nextTick();
  
  // Инициализируем Bootstrap модальное окно
  const modalElement = document.getElementById('ratingModal');
  if (modalElement && window.bootstrap) {
    modalInstance = new window.bootstrap.Modal(modalElement);
    modalInstance.show();
  }
};

const selectRating = (rating: number) => {
  selectedRating.value = rating;
};

const getRatingText = (rating: number): string => {
  const ratingTexts = {
    1: '😞 Ужасно',
    2: '😐 Плохо', 
    3: '🙂 Нормально',
    4: '😊 Хорошо',
    5: '🤩 Отлично!'
  };
  return ratingTexts[rating as keyof typeof ratingTexts] || '';
};

const submitRating = async () => {
  if (!book.value || !selectedRating.value) return;
  
  try {
    const updatedBook = await rateBookApi(book.value.id, selectedRating.value);
    // Обновляем пользовательскую оценку
    userRating.value = selectedRating.value;
    // Обновляем рейтинг книги
    book.value.rating = updatedBook.rating;
    closeRatingModal();
  } catch (error) {
    console.error('Ошибка при оценке книги:', error);
    // Можно добавить уведомление об ошибке
  }
};

const toggleVote = async () => {
  if (!book.value || !voteInfo.value || isVoting.value) return;
  
  try {
    isVoting.value = true;
    
    if (voteInfo.value.user_voted) {
      // Отменяем голос
      const response = await removeVoteForBook(book.value.id);
      voteInfo.value = {
        vote_count: response.vote_count,
        user_voted: false
      };
    } else {
      // Отдаем голос
      const response = await voteForBook(book.value.id);
      voteInfo.value = {
        vote_count: response.vote_count,
        user_voted: true
      };
    }
  } catch (error) {
    console.error('Ошибка при голосовании:', error);
    // Можно добавить уведомление об ошибке
  } finally {
    isVoting.value = false;
  }
};

const closeRatingModal = () => {
  if (modalInstance) {
    modalInstance.hide();
  }
  showRatingModal.value = false;
  selectedRating.value = 0;
  hoverRating.value = 0;
};

// Инициализация
onMounted(async () => {
  await loadBook();
  
  // Инициализируем Bootstrap dropdown после загрузки компонента
  await nextTick();
  if (window.bootstrap) {
    const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownElements.forEach(element => {
      new window.bootstrap.Dropdown(element);
    });
  }
});
</script>

<style scoped>
.book-detail-page {
  min-height: calc(100vh - var(--header-height, 60px) - var(--footer-height, 60px));
  padding-top: var(--header-height, 60px);
  color: #fff;
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
}

/* Навигация */
.breadcrumb-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.breadcrumb-link {
  color: #a8e6cf;
  text-decoration: none;
  transition: color 0.3s ease;
}

.breadcrumb-link:hover {
  color: #fff;
}

.breadcrumb-separator {
  color: rgba(255, 255, 255, 0.5);
}

.breadcrumb-current {
  color: rgba(255, 255, 255, 0.7);
}

/* Обложка */
.book-cover-section {
  position: sticky;
  top: 2rem;
}

.book-cover-large {
  position: relative;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease;
}

.book-cover-large:hover {
  transform: translateY(-5px);
}

.book-cover-large img {
  width: 100%;
  height: auto;
  aspect-ratio: 2/3;
  object-fit: cover;
}

.premium-overlay {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #1a1a1a;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

/* Информация о книге */
.book-info-section {
  padding: 1rem 0;
}

.book-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #a8e6cf;
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

.book-author {
  font-size: 1.3rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1.5rem;
}

/* Рейтинг */
.book-rating-section {
  padding: 1.5rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.rating-display {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(168, 230, 207, 0.2);
  border-radius: 15px;
  padding: 1rem 1.5rem;
  transition: all 0.3s ease;
}

.rating-display:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(168, 230, 207, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(168, 230, 207, 0.15);
}

.rating-stars {
  display: flex;
  align-items: center;
  gap: 0.2rem;
}

.rating-star {
  font-size: 1.8rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.rating-star.active {
  color: #ffd700;
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
  animation: starGlow 2s ease-in-out infinite alternate;
}

.rating-star.inactive {
  color: rgba(255, 255, 255, 0.2);
}

@keyframes starGlow {
  from {
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3)) drop-shadow(0 0 5px rgba(255, 215, 0, 0.3));
  }
  to {
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3)) drop-shadow(0 0 15px rgba(255, 215, 0, 0.6));
  }
}

.rating-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.rating-main {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-rating-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.25rem 0.5rem;
  background: rgba(168, 230, 207, 0.1);
  border-radius: 6px;
  border: 1px solid rgba(168, 230, 207, 0.3);
  z-index: 10;
}

.user-rating-badge small {
  color: #a8e6cf !important;
  font-weight: 500;
  font-size: 0.8rem;
}

.rating-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #a8e6cf;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.rating-details {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  font-weight: 500;
}

/* Метаданные */
.book-meta-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 15px;
  padding: 1.25rem;
}

.meta-item {
  display: flex;
  align-items: center;
  padding: 0.25rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.meta-item:last-child {
  border-bottom: none;
}

.meta-label {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin-right: 0.2rem;
  flex-shrink: 0;
}

/* Специфичные отступы для разных лейблов */
.meta-item:nth-child(1) .meta-label {
  margin-right: 0.4rem; /* Отступ для "Жанр" как у возрастной категории */
}

.meta-item:nth-child(2) .meta-label {
  margin-right: 0.4rem; /* Больший отступ для "Возрастная категория" */
}

.meta-value {
  color: #a8e6cf;
  font-weight: 500;
}

/* Цена */
.price-section {
  padding: 1.5rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.price-current {
  font-size: 2rem;
  font-weight: bold;
  color: #a8e6cf;
  margin-bottom: 0.5rem;
}

.price-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.price-discount {
  color: rgba(255, 255, 255, 0.6);
  text-decoration: line-through;
}

.price-subscriber {
  color: #ffd700;
  font-weight: 500;
}

/* Действия */
.book-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 2rem;
}

.list-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.list-status-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.dropdown-menu .dropdown-item.active {
  background-color: rgba(168, 230, 207, 0.2);
  color: #a8e6cf;
  font-weight: 600;
}

.dropdown-menu .dropdown-item:hover {
  background-color: rgba(168, 230, 207, 0.1);
  color: #a8e6cf;
}

.book-actions .btn {
  border-radius: 12px;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
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
  box-shadow: 0 6px 20px rgba(168, 230, 207, 0.3);
}

.book-actions .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(168, 230, 207, 0.4);
}

.book-actions .btn-outline-primary {
  background: transparent;
  border: 2px solid rgba(168, 230, 207, 0.5);
  color: #a8e6cf;
}

.book-actions .btn-outline-primary:hover {
  background: rgba(168, 230, 207, 0.1);
  border-color: #a8e6cf;
  transform: translateY(-2px);
}

.book-actions .btn-outline-secondary {
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.8);
}

.book-actions .btn-outline-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
  color: #fff;
  transform: translateY(-2px);
}

/* Секции */
.section-title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #a8e6cf;
  margin-bottom: 1.5rem;
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -0.5rem;
  left: 0;
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #a8e6cf, transparent);
  border-radius: 2px;
}

/* Описание */
.description-content {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 15px;
  padding: 2rem;
  line-height: 1.7;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
}

/* Техническая информация */
.technical-info-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 15px;
  padding: 2rem;
}

.tech-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tech-item:last-child {
  border-bottom: none;
}

.tech-label {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
}

.tech-value {
  color: #a8e6cf;
  font-weight: 500;
}

/* Секция голосования */
.book-voting-section {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(168, 230, 207, 0.2);
  backdrop-filter: blur(10px);
}

.vote-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.vote-count {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: #a8e6cf;
  font-size: 1rem;
}

.vote-number {
  font-weight: 700;
  font-size: 1.1rem;
}

.vote-text {
  color: rgba(255, 255, 255, 0.8);
}

.btn-vote {
  border-radius: 10px;
  padding: 0.5rem 1rem;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  border: 2px solid;
}

.btn-vote.btn-outline-primary {
  border-color: #a8e6cf;
  color: #a8e6cf;
  background: transparent;
}

.btn-vote.btn-outline-primary:hover:not(:disabled) {
  background: #a8e6cf;
  color: #1a1a1a;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(168, 230, 207, 0.3);
}

.btn-vote.btn-success {
  background: #a8e6cf;
  border-color: #a8e6cf;
  color: #1a1a1a;
}

.btn-vote.btn-success:hover:not(:disabled) {
  background: #8cd3b0;
  border-color: #8cd3b0;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(168, 230, 207, 0.4);
}

.btn-vote:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

@media (max-width: 768px) {
  .vote-display {
    flex-direction: column;
    text-align: center;
  }
  
  .btn-vote {
    width: 100%;
  }
}

/* Модальное окно рейтинга */
.rating-modal {
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
  border: 1px solid rgba(168, 230, 207, 0.3);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(20px);
}

.rating-modal .modal-header {
  border-bottom: 1px solid rgba(168, 230, 207, 0.2);
  background: rgba(168, 230, 207, 0.1);
  border-radius: 20px 20px 0 0;
}

.rating-modal .modal-title {
  color: #a8e6cf;
  font-weight: 700;
  font-size: 1.3rem;
}

.rating-modal .modal-footer {
  border-top: 1px solid rgba(168, 230, 207, 0.2);
  background: rgba(255, 255, 255, 0.02);
  border-radius: 0 0 20px 20px;
}

.book-title-modal {
  color: #fff;
  font-size: 1.1rem;
  font-weight: 600;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(168, 230, 207, 0.1);
}

.rating-stars-modal {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 0;
}

.rating-star-interactive {
  font-size: 3rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
}

.rating-star-interactive.active {
  color: #ffd700;
  text-shadow: 0 0 20px rgba(255, 215, 0, 0.8);
  transform: scale(1.1);
  animation: starPulse 0.6s ease-out;
}

.rating-star-interactive.inactive {
  color: rgba(255, 255, 255, 0.3);
}

.rating-star-interactive:hover {
  transform: scale(1.2) rotate(5deg);
}

@keyframes starPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.3);
  }
  100% {
    transform: scale(1.1);
  }
}

.rating-text {
  min-height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rating-description {
  color: #a8e6cf;
  font-size: 1.2rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  animation: fadeInUp 0.3s ease-out;
}

.rating-hint {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  font-style: italic;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.btn-gradient {
  background: linear-gradient(135deg, #a8e6cf 0%, #8cd3b0 100%);
  border: none;
  color: #1a1a1a;
  font-weight: 600;
  border-radius: 12px;
  padding: 0.75rem 1.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(168, 230, 207, 0.3);
}

.btn-gradient:hover:not(:disabled) {
  background: linear-gradient(135deg, #8cd3b0 0%, #a8e6cf 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(168, 230, 207, 0.4);
  color: #1a1a1a;
}

.btn-gradient:disabled {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.4);
  box-shadow: none;
  cursor: not-allowed;
}

.btn-outline-light {
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.8);
  background: transparent;
  border-radius: 12px;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-outline-light:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
  color: #fff;
  transform: translateY(-2px);
}

/* Адаптивность */
@media (max-width: 768px) {
  .book-title {
    font-size: 2rem;
  }
  
  .book-author {
    font-size: 1.1rem;
  }
  
  .book-actions {
    flex-direction: column;
  }
  
  .book-actions .btn {
    width: 100%;
  }
  
  .meta-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .meta-label {
    min-width: auto;
  }
  
  .tech-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>