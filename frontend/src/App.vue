<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'

const route = useRoute()

const isAdminRoute = () => {
  return route.path.startsWith('/admin')
}

// Импортируем AppFooter, если нужен на всех страницах
// import AppFooter from '@/components/AppFooter.vue'
</script>

<template>
  <div id="app" class="d-flex flex-column min-vh-100 bg-dark text-light">
    <AppHeader v-if="!isAdminRoute()" />
    
    <main class="flex-grow-1">
      <RouterView />
    </main>
    
    <AppFooter />
  </div>
</template>

<style>
/* Bootstrap styles are imported in main.ts */
/* Custom styles for dark/pastel theme can go here or in a separate file */
</style>
