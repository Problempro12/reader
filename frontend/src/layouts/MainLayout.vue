<template>
  <div class="main-layout dark:bg-gray-900 dark:text-gray-200 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-grow px-4 py-8">
      <router-view />
    </main>

    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import AppHeader from '../components/AppHeader.vue';
import AppFooter from '../components/AppFooter.vue';
// Логика, если нужна для основного макета
</script>

<style scoped>
/* Базовые стили для основного макета - Tailwind классы достаточны */
/* Удаляем старые стили контейнера */
</style> 