<template>
  <div class="book-of-week" v-if="bookOfWeek">
    <div class="book-of-week-header">
      <div class="header-left">
        <h3 class="book-of-week-title">
          <i class="bi bi-star-fill text-warning me-2"></i>
          Книга недели
        </h3>
        <div class="week-period" v-if="bookOfWeek.week_start && bookOfWeek.week_end">
          {{ formatWeekPeriod(bookOfWeek.week_start, bookOfWeek.week_end) }}
        </div>
      </div>
      <RouterLink 
        :to="`/books/${bookOfWeek.id}`" 
        class="btn btn-primary btn-sm"
      >
        Читать
      </RouterLink>
    </div>
    
    <div class="book-of-week-content">
      <div class="book-cover">
        <img 
          :src="bookOfWeek.cover || '/placeholder-book.svg'" 
          :alt="bookOfWeek.title"
          class="cover-image"
        />
      </div>
      
      <div class="book-info">
        <RouterLink 
          :to="`/books/${bookOfWeek.id}`" 
          class="book-title-link"
        >
          <h4 class="book-title">{{ bookOfWeek.title }}</h4>
        </RouterLink>
        
        <p class="book-author">{{ bookOfWeek.author?.name }}</p>
        
        <div class="book-icons">
          <span v-if="bookOfWeek.genre" class="icon-item">
            <i class="bi bi-tags"></i> {{ bookOfWeek.genre }}
          </span>
          <span v-if="bookOfWeek.ageCategory" class="icon-item">
            <i class="bi bi-person-check"></i> {{ bookOfWeek.ageCategory }}
          </span>
          <span v-if="bookOfWeek.rating" class="icon-item" :title="`Рейтинг: ${bookOfWeek.rating}`">
            <i class="bi bi-star-fill text-warning"></i>
            {{ bookOfWeek.rating }}
          </span>
        </div>

        <div class="book-additional-info" v-if="bookOfWeek.series || bookOfWeek.translator || bookOfWeek.technical?.year || bookOfWeek.technical?.volume || bookOfWeek.votes_at_selection">
          <div class="additional-item" v-if="bookOfWeek.series">
            <i class="bi bi-collection"></i>
            <span class="info-label">Серия:</span>
            <span>{{ bookOfWeek.series }}</span>
          </div>
          
          <div class="additional-item" v-if="bookOfWeek.translator">
            <i class="bi bi-translate"></i>
            <span class="info-label">Переводчик:</span>
            <span>{{ bookOfWeek.translator }}</span>
          </div>

          <div class="additional-item" v-if="bookOfWeek.technical?.year">
            <i class="bi bi-calendar3"></i>
            <span class="info-label">Год:</span>
            <span>{{ bookOfWeek.technical.year }}</span>
          </div>

          <div class="additional-item" v-if="bookOfWeek.technical?.volume">
            <i class="bi bi-file-earmark-text"></i>
            <span class="info-label">Объем:</span>
            <span>{{ bookOfWeek.technical.volume }}</span>
          </div>

          <div class="additional-item" v-if="bookOfWeek.votes_at_selection">
            <i class="bi bi-hand-thumbs-up"></i>
            <span class="info-label">Голосов:</span>
            <span>{{ bookOfWeek.votes_at_selection }}</span>
          </div>
        </div>
        
        <p class="book-description" v-if="bookOfWeek.description">
          {{ truncateDescription(bookOfWeek.description, 180) }}
        </p>
      </div>
    </div>
  </div>
  
  <div class="book-of-week-placeholder" v-else-if="!loading">
    <div class="placeholder-content">
      <i class="bi bi-book text-muted"></i>
      <p class="text-muted">Книга недели не выбрана</p>
    </div>
  </div>
  
  <div class="book-of-week-loading" v-else>
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Загрузка...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import { getBookOfWeek } from '@/api/books';
import type { Book } from '@/types/book';

interface BookOfWeekData extends Book {
  is_book_of_week?: boolean;
  week_start?: string;
  week_end?: string;
  votes_at_selection?: number;
}

const bookOfWeek = ref<BookOfWeekData | null>(null);
const loading = ref(true);

const fetchBookOfWeek = async () => {
  try {
    loading.value = true;
    const book = await getBookOfWeek();

    bookOfWeek.value = book as BookOfWeekData;
  } catch (error) {
    console.error('Ошибка при получении книги недели:', error);
    bookOfWeek.value = null;
  } finally {
    loading.value = false;
  }
};

const formatWeekPeriod = (startDate: string, endDate: string) => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short'
    });
  };
  
  return `${formatDate(start)} - ${formatDate(end)}`;
};

const truncateDescription = (text: string, maxLength: number) => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
};



onMounted(() => {
  fetchBookOfWeek();
});
</script>

<style scoped>
.book-of-week {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 16px;
  color: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-height: 270px; 
  overflow: hidden;
  margin-top: -50px;
}

.book-of-week-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.book-of-week-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.week-period {
  background: rgba(255, 255, 255, 0.15);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  align-self: flex-start;
  margin-top: 6px;
}

.book-of-week-content {
  display: flex;
  gap: 16px;
}

.book-cover {
  flex-shrink: 0;
  width: 100px; /* Уменьшаем ширину обложки */
  height: 150px; /* Уменьшаем высоту обложки */
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-info {
  flex-grow: 1;
  min-width: 0;
}

.book-title-link {
  text-decoration: none;
  color: inherit;
  transition: color 0.2s ease-in-out;
}

.book-title-link:hover {
  color: var(--bs-primary);
}

.book-title {
  font-size: 1.35rem;
  font-weight: 600;
  margin-bottom: 4px;
  line-height: 1.2;
}

.book-author {
  font-size: 0.9rem;
  opacity: 0.7;
  margin-bottom: 8px;
}

.book-icons {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
}

.icon-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.book-additional-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* Две колонки */
  gap: 6px;
  margin-bottom: 12px;
}

.additional-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.info-label {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}



.book-description {
  font-size: 0.85rem;
  line-height: 1.4;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 8px;
  max-height: 80px; /* Увеличиваем максимальную высоту для описания */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 4; /* Ограничение до 4 строк */
  -webkit-box-orient: vertical;
}

.btn-primary {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 6px;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  white-space: nowrap;
}

.btn-primary:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.4);
  color: white;
  transform: translateY(-1px);
}

.book-of-week-placeholder,
.book-of-week-loading {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 220px; /* Устанавливаем такую же высоту, как у основного блока */
  margin-top: 20px;
}

.placeholder-content {
  text-align: center;
  opacity: 0.7;
}

.placeholder-content .bi {
  font-size: 3rem;
  margin-bottom: 10px;
}

@media (max-width: 768px) {
  .book-of-week {
    padding: 12px;
  }
  
  .book-of-week-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .book-of-week-title {
    font-size: 1rem;
  }
  
  .week-period {
    font-size: 0.7rem;
  }
  
  .book-of-week-content {
    gap: 10px;
  }
  
  .cover-image {
    width: 50px;
    height: 67px;
  }
  
  .book-title {
    font-size: 0.9rem;
  }
  
  .book-author {
    font-size: 0.8rem;
  }
  
  .stat-item {
    font-size: 0.7rem;
  }
}
</style>