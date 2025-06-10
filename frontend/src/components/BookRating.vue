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
    <div class="rating-info" v-if="averageRating > 0">
      <span class="average-rating">{{ averageRating.toFixed(1) }}</span>
      <span class="rating-count">({{ ratingCount }} оценок)</span>
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
        const response = await axios.get(`/api/books/${this.bookId}/rating/`);
        this.userRating = response.data.user_rating;
        this.averageRating = response.data.average_rating;
        this.ratingCount = response.data.rating_count;
      } catch (error) {
        console.error('Ошибка при получении рейтинга:', error);
      }
    },
    async rateBook(rating) {
      try {
        await axios.post(`/api/books/${this.bookId}/rate/`, { rating });
        await this.fetchRating();
      } catch (error) {
        console.error('Ошибка при оценке книги:', error);
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

.star:hover {
  transform: scale(1.1);
}

.rating-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
}

.average-rating {
  font-weight: bold;
  color: #333;
}

.rating-count {
  font-size: 0.9rem;
}
</style> 