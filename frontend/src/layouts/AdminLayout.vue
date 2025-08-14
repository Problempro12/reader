<template>
  <div class="admin-layout">
    <nav class="admin-nav">
      <div class="admin-nav-header">
        <h1>Админ-панель</h1>
      </div>
      <div class="admin-nav-menu">
        <router-link to="/admin" class="admin-nav-item" active-class="active">
          <i class="bi bi-book"></i>
          <span>Книги</span>
        </router-link>
        
        <div class="admin-nav-section">
          <div class="admin-nav-section-title">Действия</div>
          <button class="admin-nav-action" @click="handleAddBook">
            <i class="bi bi-plus-lg"></i>
            <span>Добавить книгу</span>
          </button>
          <button class="admin-nav-action" @click="handleRunImport">
            <i class="bi bi-download"></i>
            <span>Запустить импорт</span>
          </button>
          <button class="admin-nav-action" @click="handleSearchFlibusta">
            <i class="bi bi-search"></i>
            <span>Поиск в Флибусте</span>
          </button>
          <button class="admin-nav-action" @click="handleBulkImport">
            <i class="bi bi-collection"></i>
            <span>Массовый импорт</span>
          </button>
          <button class="admin-nav-action danger" @click="handleDeleteAll">
            <i class="bi bi-trash"></i>
            <span>Удалить все книги</span>
          </button>
        </div>
      </div>
    </nav>
    <main class="admin-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { provide, ref } from 'vue'

// Создаем реактивные ссылки для методов дочернего компонента
const childMethods = ref<{
  openCreateModal: (() => void) | null,
  handleRunImport: (() => void) | null,
  openSearchModal: (() => void) | null,
  openBulkImportModal: (() => void) | null,
  handleDeleteAllBooks: (() => void) | null
}>({
  openCreateModal: null,
  handleRunImport: null,
  openSearchModal: null,
  openBulkImportModal: null,
  handleDeleteAllBooks: null
})

// Предоставляем функцию для регистрации методов дочернего компонента
provide('registerChildMethods', (methods: any) => {
  console.log('Registering child methods:', methods)
  childMethods.value = methods
})

const handleAddBook = () => {
  console.log('handleAddBook clicked')
  if (childMethods.value.openCreateModal) {
    childMethods.value.openCreateModal()
  } else {
    console.error('openCreateModal method not found')
  }
}

const handleRunImport = () => {
  console.log('handleRunImport clicked')
  if (childMethods.value.handleRunImport) {
    childMethods.value.handleRunImport()
  } else {
    console.error('handleRunImport method not found')
  }
}

const handleSearchFlibusta = () => {
  console.log('handleSearchFlibusta clicked')
  if (childMethods.value.openSearchModal) {
    childMethods.value.openSearchModal()
  } else {
    console.error('openSearchModal method not found')
  }
}

const handleBulkImport = () => {
  console.log('handleBulkImport clicked')
  if (childMethods.value.openBulkImportModal) {
    childMethods.value.openBulkImportModal()
  } else {
    console.error('openBulkImportModal method not found')
  }
}

const handleDeleteAll = () => {
  console.log('handleDeleteAll clicked')
  if (childMethods.value.handleDeleteAllBooks) {
    childMethods.value.handleDeleteAllBooks()
  } else {
    console.error('handleDeleteAllBooks method not found')
  }
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #1a1a1a;
}

.admin-nav {
  width: 250px;
  background: #2a2a2a;
  color: #fff;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 1000;
}

.admin-nav-header {
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 1rem;
}

.admin-nav-header h1 {
  font-size: 1.5rem;
  margin: 0;
  color: #fff;
}

.admin-nav-menu {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.admin-nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.admin-nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.admin-nav-item.active {
  background: var(--primary-color);
  color: #fff;
}

.admin-nav-item i {
  font-size: 1.2rem;
}

.admin-nav-section {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.admin-nav-section-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.75rem;
  padding: 0 1rem;
}

.admin-nav-action {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: rgba(255, 255, 255, 0.7);
  background: none;
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  width: 100%;
  text-align: left;
  cursor: pointer;
  margin-bottom: 0.25rem;
}

.admin-nav-action:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.admin-nav-action.danger {
  color: rgba(220, 53, 69, 0.8);
}

.admin-nav-action.danger:hover {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.admin-nav-action i {
  font-size: 1rem;
}

.admin-nav-action span {
  font-size: 0.9rem;
  font-weight: 500;
}

.admin-content {
  flex: 1;
  margin-left: 260px;
  min-height: 100vh;
  background: #1a1a1a;
}

@media (max-width: 768px) {
  .admin-layout {
    flex-direction: column;
  }

  .admin-nav {
    width: 100%;
    height: auto;
    position: relative;
  }

  .admin-content {
    margin-left: 0;
    padding: 1rem;
  }
}
</style>