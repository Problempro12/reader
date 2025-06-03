<template>
  <div class="auth-layout">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// Логика, если нужна для макета аутентификации
</script>

<style scoped>
.auth-layout {
  /* Базовые стили для центрирования или фона на страницах аутентификации */
  /* Убираем flexbox стили, так как центрирование есть во вложенных страницах */
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
}
</style> 