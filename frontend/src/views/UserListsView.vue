<template>
  <div class="container-fluid mb-4" style="padding-top: 80px;">
    <div class="row">
      <!-- Боковая панель -->
      <div class="col-md-3">
        <div class="sidebar-card">
          <div class="sidebar-header">
            <h5><i class="bi bi-list-ul me-2"></i>Мои списки</h5>
          </div>
          <div class="sidebar-menu">
            <button 
              v-for="list in listTypes" 
              :key="list.key"
              @click="setActiveList(list.key)"
              class="sidebar-menu-item"
              :class="{ 'active': activeList === list.key }"
            >
              <span class="menu-text">
                <i :class="list.icon" class="me-2"></i>
                {{ list.name }}
              </span>
              <span class="menu-count">{{ getListCount(list.key) }}</span>
            </button>
          </div>
        </div>

        
        <div class="sidebar-card mt-3">
          <div class="sidebar-header">
            <h6><i class="bi bi-sort-down me-2"></i>Сортировка</h6>
          </div>
          <div class="sidebar-content">
            <div class="form-check">
              <input class="form-check-input" type="radio" name="sortBy" id="sortByDate" value="date" v-model="sortBy">
              <label class="form-check-label" for="sortByDate">
                По дате добавления
              </label>
            </div>
            <div class="form-check">
              <input class="form-check-input" type="radio" name="sortBy" id="sortByTitle" value="title" v-model="sortBy">
              <label class="form-check-label" for="sortByTitle">
                По названию
              </label>
            </div>
          </div>
        </div>
      </div>

      
      <!-- Основной контент -->
      <div class="col-md-9">
        <!-- Поиск -->
        <div class="search-card mb-3">
          <div class="search-input-group">
            <span class="search-icon">
              <i class="bi bi-search"></i>
            </span>
            <input 
              type="text" 
              class="search-input" 
              placeholder="Поиск по названию или автору..."
              v-model="searchQuery"
            >
          </div>
        </div>

        
        <!-- Состояние загрузки -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Загружаем ваши списки...</p>
        </div>
        
        <!-- Ошибка -->
        <div v-else-if="error" class="error-state">
          <i class="bi bi-exclamation-triangle"></i>
          <p>{{ error }}</p>
        </div>
        
        <!-- Пустое состояние -->
        <div v-else-if="filteredBooks.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-book"></i>
          </div>
          <h4>{{ getEmptyStateMessage() }}</h4>
          <p>{{ getEmptyStateDescription() }}</p>
          <router-link to="/" class="btn btn-gradient">
            <i class="bi bi-plus-circle me-2"></i>
            Перейти к каталогу
          </router-link>
        </div>

        
        <!-- Список книг -->
        <div v-else class="books-grid">
          <div v-for="userBook in filteredBooks" :key="userBook.id" class="book-card">
            <div class="book-cover">
              <img 
                :src="userBook.book.cover_url || '/placeholder-book.svg'" 
                :alt="userBook.book.title"
                @error="handleImageError"
              >
            </div>
            <div class="book-info">
              <div class="book-header">
                <h5 class="book-title">
                  <router-link :to="`/books/${userBook.book.id}`">
                    {{ userBook.book.title }}
                  </router-link>
                </h5>
                <div class="book-actions">
                  <button class="action-btn" @click="toggleDropdown(userBook.id)">
                    <i class="bi bi-three-dots"></i>
                  </button>
                  <div class="dropdown-menu" :class="{ 'show': activeDropdown === userBook.id }">
                    <button @click="changeStatus(userBook, 'reading')" class="dropdown-item">
                      <i class="bi bi-book-half me-2"></i>Читаю
                    </button>
                    <button @click="changeStatus(userBook, 'planned')" class="dropdown-item">
                      <i class="bi bi-bookmark me-2"></i>В планах
                    </button>
                    <button @click="changeStatus(userBook, 'completed')" class="dropdown-item">
                      <i class="bi bi-check-circle me-2"></i>Прочитано
                    </button>
                    <button @click="changeStatus(userBook, 'dropped')" class="dropdown-item">
                      <i class="bi bi-x-circle me-2"></i>Брошено
                    </button>
                    <hr>
                    <button @click="removeFromList(userBook)" class="dropdown-item danger">
                      <i class="bi bi-trash me-2"></i>Удалить из списка
                    </button>
                  </div>
                </div>
              </div>
              <p class="book-author" v-if="userBook.book.author">
                <i class="bi bi-person me-1"></i>
                {{ userBook.book.author.name }}
              </p>
              <div class="book-meta">
                <span class="book-status" :class="getStatusClass(userBook.status)">
                  <i :class="getStatusIcon(userBook.status)" class="me-1"></i>
                  {{ getStatusName(userBook.status) }}
                </span>
                <small class="book-date">
                  <i class="bi bi-calendar-plus me-1"></i>
                  {{ formatDate(userBook.added_at) }}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getUserBooks, updateUserBookStatus, removeUserBook } from '@/api/books'

interface UserBook {
  id: number
  book: {
    id: number
    title: string
    author: {
      id: number
      name: string
    }
    cover_url?: string
  }
  status: string
  rating?: number
  added_at: string
}

const userBooks = ref<UserBook[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const activeList = ref('all')
const searchQuery = ref('')
const sortBy = ref('date')
const activeDropdown = ref<number | null>(null)

// Типы списков
const listTypes = [
  { key: 'all', name: 'Все книги', icon: 'bi bi-collection' },
  { key: 'reading', name: 'Читаю', icon: 'bi bi-book-half' },
  { key: 'planned', name: 'В планах', icon: 'bi bi-bookmark' },
  { key: 'completed', name: 'Прочитано', icon: 'bi bi-check-circle' },
  { key: 'dropped', name: 'Брошено', icon: 'bi bi-x-circle' }
]

// Вычисляемые свойства для подсчета книг
const getListCount = (listType: string) => {
  if (listType === 'all') return userBooks.value.length
  return userBooks.value.filter(book => book.status === listType).length
}

// Фильтрация книг
const filteredBooks = computed(() => {
  let books = userBooks.value
  
  // Фильтрация по активному списку
  if (activeList.value !== 'all') {
    books = books.filter(book => book.status === activeList.value)
  }
  
  // Фильтрация по поисковому запросу
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    books = books.filter(book => 
      book.book.title.toLowerCase().includes(query) ||
      (book.book.author && book.book.author.name.toLowerCase().includes(query))
    )
  }
  
  // Сортировка
  if (sortBy.value === 'title') {
    books = books.sort((a, b) => a.book.title.localeCompare(b.book.title))
  } else {
    books = books.sort((a, b) => new Date(b.added_at).getTime() - new Date(a.added_at).getTime())
  }
  
  return books
})

// Установка активного списка
const setActiveList = (listType: string) => {
  activeList.value = listType
}

// Переключение выпадающего меню
const toggleDropdown = (bookId: number) => {
  activeDropdown.value = activeDropdown.value === bookId ? null : bookId
}

// Получение класса для статуса
const getStatusClass = (status: string) => {
  return status
}

// Получение класса для бейджа статуса
const getStatusBadgeClass = (status: string) => {
  const classes = {
    reading: 'bg-primary',
    planned: 'bg-warning',
    completed: 'bg-success',
    dropped: 'bg-secondary'
  }
  return classes[status as keyof typeof classes] || 'bg-secondary'
}

// Получение иконки для статуса
const getStatusIcon = (status: string) => {
  const icons = {
    reading: 'bi bi-book-half',
    planned: 'bi bi-bookmark',
    completed: 'bi bi-check-circle',
    dropped: 'bi bi-x-circle'
  }
  return icons[status as keyof typeof icons] || 'bi bi-question-circle'
}

// Получение названия статуса
const getStatusName = (status: string) => {
  const names = {
    reading: 'Читаю',
    planned: 'В планах',
    completed: 'Прочитано',
    dropped: 'Брошено'
  }
  return names[status as keyof typeof names] || status
}

// Изменение статуса книги
const changeStatus = async (userBook: UserBook, newStatus: string) => {
  try {
    await updateUserBookStatus(userBook.id, newStatus)
    userBook.status = newStatus
  } catch (err) {
    console.error('Ошибка при изменении статуса:', err)
    error.value = 'Не удалось изменить статус книги'
  }
}

// Удаление книги из списка
const removeFromList = async (userBook: UserBook) => {
  if (!confirm('Вы уверены, что хотите удалить эту книгу из списка?')) {
    return
  }
  
  try {
    await removeUserBook(userBook.id)
    const index = userBooks.value.findIndex(book => book.id === userBook.id)
    if (index !== -1) {
      userBooks.value.splice(index, 1)
    }
  } catch (err) {
    console.error('Ошибка при удалении книги:', err)
    error.value = 'Не удалось удалить книгу из списка'
  }
}

// Загрузка списков пользователя
const loadUserBooks = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await getUserBooks()
    userBooks.value = response
  } catch (err) {
    console.error('Ошибка при загрузке списков:', err)
    error.value = 'Не удалось загрузить списки книг'
  } finally {
    loading.value = false
  }
}

// Обработка ошибки загрузки изображения
const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  target.src = '/placeholder-book.svg'
}

// Форматирование даты
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

// Сообщения для пустого состояния
const getEmptyStateMessage = () => {
  if (searchQuery.value.trim()) {
    return 'Ничего не найдено'
  }
  
  switch (activeList.value) {
    case 'reading':
      return 'Вы пока ничего не читаете'
    case 'planned':
      return 'У вас нет книг в планах'
    case 'completed':
      return 'Вы пока не прочитали ни одной книги'
    case 'dropped':
      return 'У вас нет брошенных книг'
    default:
      return 'У вас пока нет книг в списках'
  }
}

const getEmptyStateDescription = () => {
  if (searchQuery.value.trim()) {
    return 'Попробуйте изменить поисковый запрос'
  }
  
  switch (activeList.value) {
    case 'reading':
      return 'Добавьте книги в список "Читаю" из каталога'
    case 'planned':
      return 'Добавьте книги, которые планируете прочитать'
    case 'completed':
      return 'Отмечайте прочитанные книги как "Прочитано"'
    case 'dropped':
      return 'Здесь будут книги, которые вы не дочитали'
    default:
      return 'Начните добавлять книги из каталога в свои списки'
  }
}

onMounted(() => {
  loadUserBooks()
})
</script>

<style scoped>
.sidebar-card {
  background: var(--bg-white);
  border-radius: 12px;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
}

.sidebar-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-light);
  border-radius: 12px 12px 0 0;
}

.sidebar-header h5, .sidebar-header h6 {
  margin: 0;
  color: var(--text-color);
  font-weight: 600;
}

.sidebar-menu {
  padding: 0;
}

.sidebar-menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-color);
}

.sidebar-menu-item:last-child {
  border-bottom: none;
}

.sidebar-menu-item:hover {
  background: var(--bg-light);
}

.sidebar-menu-item.active {
  background: var(--primary-color);
  color: var(--primary-dark);
  font-weight: 500;
}

.menu-text {
  display: flex;
  align-items: center;
}

.menu-count {
  background: var(--border-color);
  color: var(--text-color);
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.sidebar-menu-item.active .menu-count {
  background: var(--primary-dark);
  color: white;
}

.sidebar-content {
  padding: 1rem 1.5rem;
}

.form-check {
  margin-bottom: 0.75rem;
  position: relative;
}

.form-check:last-child {
  margin-bottom: 0;
}

.form-check-input {
  appearance: none;
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-color);
  border-radius: 50%;
  background: var(--bg-white);
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 0.125rem;
}

.form-check-input:checked {
  border-color: var(--primary-color);
  background: var(--primary-color);
  position: relative;
}

.form-check-input:checked::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary-dark);
}

.form-check-input:hover {
  border-color: var(--primary-color);
}

.form-check-label {
  margin-left: 0.75rem;
  cursor: pointer;
  color: var(--text-color);
  font-weight: 500;
  transition: color 0.2s ease;
}

.form-check-label:hover {
  color: var(--primary-color);
}

.search-card {
  background: var(--bg-white);
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
}

.search-input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: var(--text-light);
  z-index: 2;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
  background: var(--bg-white);
  color: var(--text-color);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 3rem 1rem;
  background: var(--bg-white);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  color: var(--text-color);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state i {
  font-size: 3rem;
  color: var(--danger-color);
  margin-bottom: 1rem;
}

.empty-icon i {
  font-size: 4rem;
  color: var(--text-light);
  margin-bottom: 1rem;
}

.books-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.book-card {
  display: flex;
  background: var(--bg-white);
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.book-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.book-cover {
  flex-shrink: 0;
  margin-right: 1rem;
}

.book-cover img {
  width: 80px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.book-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.book-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.book-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.book-title a {
  color: var(--text-color);
  text-decoration: none;
}

.book-title a:hover {
  color: var(--primary-color);
}

.book-actions {
  position: relative;
}

.action-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

.action-btn:hover {
  background: var(--bg-light);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--bg-white);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  min-width: 180px;
  display: none;
}

.dropdown-menu.show {
  display: block;
}

.dropdown-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.5rem 1rem;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.dropdown-item:hover {
  background: var(--bg-light);
}

.dropdown-item.danger {
  color: var(--danger-color);
}

.dropdown-item.danger:hover {
  background: rgba(255, 107, 107, 0.1);
}

.book-author {
  color: var(--text-light);
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.book-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: auto;
}

.book-status {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.book-status.reading {
  background: rgba(127, 176, 105, 0.12);
  color: var(--primary-dark);
}

.book-status.planned {
  background: rgba(255, 193, 7, 0.1);
  color: #856404;
}

.book-status.completed {
  background: rgba(40, 167, 69, 0.1);
  color: #155724;
}

.book-status.dropped {
  background: rgba(108, 117, 125, 0.1);
  color: #495057;
}

.book-date {
  color: var(--text-light);
  font-size: 0.8rem;
}
</style>