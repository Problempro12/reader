<template>
  <div class="top-books-voting">
    <h3 class="voting-title">Топ-5 книг по голосам</h3>
    <div class="books-list" v-if="topBooks.length > 0">
      <div 
        v-for="(book, index) in topBooks" 
        :key="book.id" 
        class="book-item"
        :class="{ 'voted': hasVoted(book.id) }"
      >
        <div class="book-rank">{{ index + 1 }}</div>
        <div class="book-content">
          <RouterLink 
            :to="`/app/books/${book.id}`" 
            class="book-title-link"
          >
            {{ book.title }}
          </RouterLink>
          <div class="book-votes">
            <i class="bi bi-hand-thumbs-up"></i>
            <span>{{ book.vote_count || 0 }}</span>
          </div>
        </div>
        <button 
          class="btn btn-vote-small"
          :class="hasVoted(book.id) ? 'btn-success' : 'btn-outline-primary'"
          @click="toggleVote(book)"
          :disabled="isVoting"
        >
          <i class="bi" :class="hasVoted(book.id) ? 'bi-hand-thumbs-up-fill' : 'bi-hand-thumbs-up'"></i>
        </button>
      </div>
    </div>
    <div v-else class="no-books">
      <p>Нет данных о голосовании</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import { getTopVotedBooks, voteForBook, removeVoteForBook, getBookVoteInfo } from '@/api/books';
import type { Book } from '@/types/book';

interface BookWithVotes extends Book {
  vote_count?: number;
}

const topBooks = ref<BookWithVotes[]>([]);
const votedBooks = ref<number[]>([]);
const isVoting = ref(false);

const fetchTopBooks = async () => {
  try {
    const books = await getTopVotedBooks(5);
    topBooks.value = books;
    
    // Получаем информацию о голосах для каждой книги
    for (const book of books) {
      try {
        const voteInfo = await getBookVoteInfo(book.id);
        book.vote_count = voteInfo.vote_count;
        if (voteInfo.user_voted) {
          votedBooks.value.push(book.id);
        }
      } catch (error) {
        console.error(`Ошибка при получении информации о голосах для книги ${book.id}:`, error);
      }
    }
  } catch (error) {
    console.error('Ошибка при получении топ книг:', error);
  }
};

const hasVoted = (bookId: number) => {
  return votedBooks.value.includes(bookId);
};

const toggleVote = async (book: BookWithVotes) => {
  if (isVoting.value) return;
  
  isVoting.value = true;
  try {
    if (hasVoted(book.id)) {
      await removeVoteForBook(book.id);
      votedBooks.value = votedBooks.value.filter(id => id !== book.id);
      if (book.vote_count) {
        book.vote_count--;
      }
    } else {
      await voteForBook(book.id);
      votedBooks.value.push(book.id);
      book.vote_count = (book.vote_count || 0) + 1;
    }
  } catch (error) {
    console.error('Ошибка при голосовании:', error);
  } finally {
    isVoting.value = false;
  }
};

onMounted(() => {
  fetchTopBooks();
});
</script>

<style scoped>
.top-books-voting {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 230, 207, 0.2);
  border-radius: 15px;
  padding: 1rem;
  backdrop-filter: blur(10px);
}

.voting-title {
  color: #a8e6cf;
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-align: center;
}

.books-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.book-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.book-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(168, 230, 207, 0.3);
}

.book-item.voted {
  border-color: #a8e6cf;
  background: rgba(168, 230, 207, 0.1);
}

.book-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #a8e6cf;
  color: #1a1a1a;
  border-radius: 50%;
  font-weight: bold;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.book-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.book-title-link {
  color: #fff;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  line-height: 1.2;
  transition: color 0.3s ease;
}

.book-title-link:hover {
  color: #a8e6cf;
  text-decoration: underline;
}

.book-votes {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.75rem;
}

.book-votes i {
  color: #a8e6cf;
}

.btn-vote-small {
  padding: 0.375rem;
  border-radius: 8px;
  border: 1px solid rgba(168, 230, 207, 0.3);
  background: transparent;
  color: #a8e6cf;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.btn-vote-small:hover {
  background: rgba(168, 230, 207, 0.1);
  border-color: #a8e6cf;
}

.btn-vote-small.btn-success {
  background: #a8e6cf;
  border-color: #a8e6cf;
  color: #1a1a1a;
}

.btn-vote-small.btn-success:hover {
  background: #8cd3b0;
  border-color: #8cd3b0;
}

.no-books {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  padding: 1rem;
}

@media (max-width: 768px) {
  .top-books-voting {
    padding: 1rem;
  }
  
  .voting-title {
    font-size: 1rem;
  }
  
  .book-item {
    padding: 0.5rem;
    gap: 0.5rem;
  }
  
  .book-title-link {
    font-size: 0.8rem;
  }
}
</style>