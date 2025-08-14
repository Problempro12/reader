<template>
  <div class="book-rating">
    <div class="stars" @mouseleave="resetHover">
      <span
        v-for="star in 5"
        :key="star"
        class="star"
        :class="{ 'active': star <= (hoverRating || userRating || 0) }"
        @mouseover="hoverRating = star"
        @click="rateBook(star)"
      >
        ★
      </span>
    </div>
    <div class="rating-info">
      <div v-if="averageRating > 0">
        <span class="average-rating">{{ averageRating.toFixed(1) }}</span>
        <span class="rating-count">({{ ratingCount }} оценок)</span>
      </div>
      <div v-if="userRating > 0" class="user-rating-info">
        <span class="user-rating-text">Ваша оценка: {{ userRating }} ★</span>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'BookRating',
  props: {
    bookId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      userRating: 0,
      averageRating: 0,
      ratingCount: 0,
      hoverRating: 0
    };
  },
  async created() {
    await this.fetchRating();
  },
  methods: {
    async fetchRating() {
      try {
        const token = localStorage.getItem('token');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        
        const response = await axios.get(`/api/books/${this.bookId}/rating/`, {
          headers
        });
        this.userRating = response.data.user_rating || 0;
        this.averageRating = response.data.average_rating || 0;
        this.ratingCount = response.data.rating_count || 0;
      } catch (error) {
        console.error('Ошибка при получении рейтинга:', error);
      }
    },
    async rateBook(rating) {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          alert('Для оценки книги необходимо войти в систему');
          return;
        }
        
        await axios.post(`/api/books/${this.bookId}/rate/`, 
          { rating },
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        await this.fetchRating();
      } catch (error) {
        console.error('Ошибка при оценке книги:', error);
        if (error.response?.status === 401) {
          alert('Для оценки книги необходимо войти в систему');
        }
      }
    },
    resetHover() {
      this.hoverRating = 0;
    }
  }
};
</script>

<style scoped>
.book-rating {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stars {
  display: flex;
  gap: 0.25rem;
}

.star {
  font-size: 1.5rem;
  color: #ddd;
  cursor: pointer;
  transition: color 0.2s;
}

.star.active {
  color: #ffd700;
}



.rating-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  color: #666;
}

.rating-info > div {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-rating-info {
  font-size: 0.9rem;
  color: var(--primary-color);
  font-weight: 500;
}

.user-rating-text {
  color: var(--primary-color);
}

.average-rating {
  font-weight: bold;
  color: #333;
}

.rating-count {
  font-size: 0.9rem;
}
</style>