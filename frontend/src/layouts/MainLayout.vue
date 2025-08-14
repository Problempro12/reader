<template>
  <div class="main-layout bg-dark text-light min-vh-100 d-flex flex-column">
    <AppHeader />

    <main class="flex-grow-1 px-4 py-4">
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