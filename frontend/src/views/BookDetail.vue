<template>
  <div class="book-detail">
    <h1>{{ book.title }}</h1>
    <p><strong>Автор:</strong> {{ book.author }}</p>
    <p><strong>Описание:</strong> {{ book.description }}</p>
    <button @click="startReading">Начать чтение</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const book = ref({ title: '', author: '', description: '' });

const fetchBookDetails = async () => {
  try {
    const response = await fetch(`/api/books/${route.params.id}`);
    const data = await response.json();
    book.value = data;
  } catch (error) {
    console.error('Ошибка при загрузке деталей книги:', error);
  }
};

const startReading = () => {
  router.push({ name: 'book-reader', params: { id: route.params.id } });
};

onMounted(() => {
  fetchBookDetails();
});
</script>

<style scoped>
.book-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 24px;
  margin-bottom: 10px;
}

p {
  margin-bottom: 10px;
}

button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style> 