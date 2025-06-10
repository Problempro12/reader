<template>
  <div class="book-reader">
    <div class="book-content" v-html="renderedContent"></div>
    <div class="controls">
      <button @click="prevPage" :disabled="currentPage === 1">Предыдущая страница</button>
      <span>Страница {{ currentPage }} из {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages">Следующая страница</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { marked } from 'marked';

const props = defineProps<{
  bookId: string;
}>();

const renderedContent = ref('');
const currentPage = ref(1);
const totalPages = ref(1);

const fetchBookContent = async () => {
  try {
    const response = await fetch(`/api/books/${props.bookId}/content`);
    const data = await response.json();
    renderedContent.value = marked(data.content);
    totalPages.value = data.totalPages;
  } catch (error) {
    console.error('Ошибка при загрузке книги:', error);
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchBookContent();
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    fetchBookContent();
  }
};

onMounted(() => {
  fetchBookContent();
});
</script>

<style scoped>
.book-reader {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.book-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  width: 100%;
  max-width: 800px;
}

button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

span {
  font-size: 16px;
}
</style> 