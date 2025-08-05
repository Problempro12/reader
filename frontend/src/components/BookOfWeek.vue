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
        
        <div class="book-meta" v-if="bookOfWeek.technical?.year || bookOfWeek.genre || bookOfWeek.ageCategory">
          <div class="meta-item" v-if="bookOfWeek.technical?.year">
            <i class="bi bi-calendar3"></i>
            <span>{{ bookOfWeek.technical.year }} год</span>
          </div>
          
          <div class="meta-item" v-if="bookOfWeek.genre">
            <i class="bi bi-tags"></i>
            <span>{{ bookOfWeek.genre }}</span>
          </div>
          
          <div class="meta-item" v-if="bookOfWeek.ageCategory">
            <i class="bi bi-person-check"></i>
            <span>{{ bookOfWeek.ageCategory }}</span>
          </div>
        </div>
        
        <div class="book-additional-info" v-if="bookOfWeek.series || bookOfWeek.translator">
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
        </div>
        
        <div class="book-stats">
          <div class="stat-item" v-if="bookOfWeek.votes_at_selection">
            <i class="bi bi-hand-thumbs-up"></i>
            <span>{{ bookOfWeek.votes_at_selection }} голосов</span>
          </div>
          
          <div class="stat-item" v-if="bookOfWeek.rating">
            <i class="bi bi-star-fill text-warning"></i>
            <span>{{ bookOfWeek.rating }}</span>
          </div>
          
          <div class="stat-item" v-if="bookOfWeek.technical?.volume">
            <i class="bi bi-file-earmark-text"></i>
            <span>{{ bookOfWeek.technical.volume }}</span>
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
  padding: 12px;
  color: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
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
  gap: 20px;
  align-items: flex-start;
}

.book-cover {
  flex-shrink: 0;
}

.cover-image {
  width: 120px;
  height: 168px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.book-info {
  flex: 1;
  min-width: 0;
}

.book-title-link {
  text-decoration: none;
  color: inherit;
}

.book-title-link:hover .book-title {
  text-decoration: underline;
}

.book-title {
  margin: 0 0 8px 0;
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.3;
}

.book-author {
  margin: 0 0 12px 0;
  font-size: 1rem;
  opacity: 0.9;
  font-weight: 500;
}

.book-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.875rem;
  opacity: 0.9;
}

.book-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.875rem;
  opacity: 0.9;
}

.book-description {
  margin: 0 0 16px 0;
  font-size: 0.9rem;
  line-height: 1.5;
  opacity: 0.9;
}

.book-additional-info {
  margin-bottom: 12px;
}

.additional-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  opacity: 0.9;
  margin-bottom: 6px;
}

.additional-item:last-child {
  margin-bottom: 0;
}

.info-label {
  font-weight: 500;
  min-width: 80px;
}



.book-description-old {
  margin: 0 0 16px 0;
  font-size: 0.9rem;
  line-height: 1.5;
  opacity: 0.9;
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
  background: rgba(248, 249, 250, 0.1);
  border: 2px dashed rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  padding: 30px;
  text-align: center;
  color: white;
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.placeholder-content i {
  font-size: 2rem;
}

.placeholder-content p {
  margin: 0;
  font-size: 1rem;
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