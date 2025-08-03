<template>
  <div class="admin-books">
    <div class="admin-header">
      <h2>Управление книгами</h2>
      <div class="header-buttons">
        <button class="btn btn-primary" @click="openCreateModal">
          <i class="bi bi-plus-lg"></i>
          Добавить книгу
        </button>
        <button class="btn btn-secondary" @click="handleRunImport">
          <i class="bi bi-download"></i>
          Запустить импорт
        </button>
      </div>
    </div>

    <div class="admin-filters">
      <div class="search-box">
        <i class="bi bi-search"></i>
        <input
          type="text"
          v-model="filters.search"
          placeholder="Поиск по названию или автору"
          @input="handleSearch"
        />
      </div>
      <div class="filter-group">
        <select v-model="filters.genre" @change="loadBooks">
          <option value="">Все жанры</option>
          <option v-for="genre in genres" :key="genre" :value="genre">
            {{ genre }}
          </option>
        </select>
        <select v-model="filters.ageCategory" @change="loadBooks">
          <option value="">Все возрастные категории</option>
          <option v-for="category in ageCategories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>
    </div>

    <div class="admin-table">
      <table>
        <thead>
          <tr>
            <th>Обложка</th>
            <th>Название</th>
            <th>Автор</th>
            <th>Жанр</th>
            <th>Возраст</th>
            <th>Рейтинг</th>
            <th>Премиум</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="book in books" :key="book.id">
            <td>
              <img :src="book.cover" :alt="book.title" class="book-cover" @error="handleImageError" />
            </td>
            <td>{{ book.title }}</td>
            <td>{{ book.author }}</td>
            <td>{{ book.genre }}</td>
            <td>{{ book.ageCategory }}</td>
            <td>{{ typeof book.rating === 'number' ? book.rating.toFixed(1) : '0.0' }}</td>
            <td>
              <span class="badge" :class="{ premium: book.isPremium }">
                {{ book.isPremium ? 'Да' : 'Нет' }}
              </span>
            </td>
            <td>
              <div class="actions">
                <button class="btn btn-sm btn-edit" @click="openEditModal(book)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-delete" @click="confirmDelete(book)">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button
        class="btn"
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        <i class="bi bi-chevron-left"></i>
      </button>
      <span>Страница {{ currentPage }} из {{ totalPages }}</span>
      <button
        class="btn"
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        <i class="bi bi-chevron-right"></i>
      </button>
    </div>

    <!-- Модальное окно создания/редактирования книги -->
    <div class="modal" v-if="showModal">
      <div class="modal-content">
        <h3>{{ editingBook ? 'Редактировать книгу' : 'Добавить книгу' }}</h3>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>Название</label>
            <input type="text" v-model="form.title" required />
          </div>
          <div class="form-group">
            <label>Автор</label>
            <input type="text" v-model="form.author" required />
          </div>
          <div class="form-group">
            <label>Обложка (URL)</label>
            <input type="url" v-model="form.cover" required />
          </div>
          <div class="form-group">
            <label>Жанр</label>
            <select v-model="form.genre" required>
              <option v-for="genre in genres" :key="genre" :value="genre">
                {{ genre }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Возрастная категория</label>
            <select v-model="form.ageCategory" required>
              <option v-for="category in ageCategories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Описание</label>
            <textarea v-model="form.description" rows="4" required></textarea>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.isPremium" />
              Премиум книга
            </label>
          </div>
          <div class="form-group">
            <label>Серия</label>
            <input type="text" v-model="form.series" />
          </div>
          <div class="form-group">
            <label>Переводчик</label>
            <input type="text" v-model="form.translator" />
          </div>
          <div class="form-group">
            <label>Техническая информация</label>
            <div class="technical-info">
              <input type="text" v-model="technicalVolume" placeholder="Объем" />
              <input type="text" v-model="technicalYear" placeholder="Год издания" />
              <input type="text" v-model="technicalIsbn" placeholder="ISBN" />
              <input type="text" v-model="technicalCopyrightHolder" placeholder="Правообладатель" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn" @click="closeModal">Отмена</button>
            <button type="submit" class="btn btn-primary">
              {{ editingBook ? 'Сохранить' : 'Добавить' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <div class="modal" v-if="showDeleteModal">
      <div class="modal-content">
        <h3>Подтверждение удаления</h3>
        <p>Вы уверены, что хотите удалить книгу "{{ bookToDelete?.title }}"?</p>
        <div class="modal-actions">
          <button class="btn" @click="closeDeleteModal">Отмена</button>
          <button class="btn btn-danger" @click="handleDelete">Удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { getBooks, createBook, updateBook, deleteBook, runImportScript } from '@/api/books'
import type { Book, BookCreate } from '@/types/book'

const books = ref<Book[]>([])
const filters = reactive({
  search: '',
  genre: '',
  ageCategory: '',
  page: 1,
  limit: 10
})

const totalPages = ref(1)
const currentPage = ref(1)
const loading = ref(false)
const error = ref<string | null>(null)

// Модальные окна
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingBook = ref<Book | null>(null)
const bookToDelete = ref<Book | null>(null)

const form = reactive<BookCreate>({
  title: '',
  author: '',
  cover: '',
  genre: '',
  ageCategory: '',
  description: '',
  isPremium: false,
  series: '',
  translator: '',
  technical: {
    volume: '',
    year: '',
    isbn: '',
    copyrightHolder: ''
  }
})

const genres = [
  'Фэнтези',
  'Научная фантастика',
  'Детектив',
  'Роман',
  'Приключения',
  'Ужасы',
  'Исторический',
  'Биография',
  'Психология',
  'Бизнес'
]

const ageCategories = [
  '6+',
  '12+',
  '16+',
  '18+'
]

const technicalVolume = computed({
  get: () => form.technical?.volume || '',
  set: (value) => {
    if (!form.technical) {
      form.technical = { volume: '', year: '', isbn: '', copyrightHolder: '' }
    }
    form.technical.volume = value
  }
})

const technicalYear = computed({
  get: () => form.technical?.year || '',
  set: (value) => {
    if (!form.technical) {
      form.technical = { volume: '', year: '', isbn: '', copyrightHolder: '' }
    }
    form.technical.year = value
  }
})

const technicalIsbn = computed({
  get: () => form.technical?.isbn || '',
  set: (value) => {
    if (!form.technical) {
      form.technical = { volume: '', year: '', isbn: '', copyrightHolder: '' }
    }
    form.technical.isbn = value
  }
})

const technicalCopyrightHolder = computed({
  get: () => form.technical?.copyrightHolder || '',
  set: (value) => {
    if (!form.technical) {
      form.technical = { volume: '', year: '', isbn: '', copyrightHolder: '' }
    }
    form.technical.copyrightHolder = value
  }
})

const loadBooks = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await getBooks(filters)
    books.value = response.books
    totalPages.value = Math.ceil(response.total / filters.limit)
    currentPage.value = filters.page
  } catch (err) {
    error.value = 'Failed to load books.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  filters.page = 1
  loadBooks()
}

const changePage = (page: number) => {
  filters.page = page
  loadBooks()
}

const openCreateModal = () => {
  editingBook.value = null
  Object.assign(form, {
    title: '',
    author: '',
    cover: '',
    genre: '',
    ageCategory: '',
    description: '',
    isPremium: false,
    series: '',
    translator: '',
    technical: {
      volume: '',
      year: '',
      isbn: '',
      copyrightHolder: ''
    }
  })
  showModal.value = true
}

const openEditModal = (book: Book) => {
  editingBook.value = book
  Object.assign(form, {
    title: book.title,
    author: book.author,
    cover: book.cover,
    genre: book.genre,
    ageCategory: book.ageCategory,
    description: book.description,
    isPremium: book.isPremium,
    series: book.series || '',
    translator: book.translator || '',
    technical: book.technical || { volume: '', year: '', isbn: '', copyrightHolder: '' }
  })
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingBook.value = null
}

const handleSubmit = async () => {
  try {
    if (editingBook.value) {
      // Обновление существующей книги
      await updateBook({ id: editingBook.value.id, ...form })
    } else {
      // Создание новой книги
      await createBook(form)
    }
    closeModal()
    await loadBooks() // Перезагружаем книги после сохранения
  } catch (err) {
    console.error('Ошибка сохранения книги:', err)
    alert('Ошибка сохранения книги.')
  }
}

const confirmDelete = (book: Book) => {
  bookToDelete.value = book
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  bookToDelete.value = null
}

const handleDelete = async () => {
  if (bookToDelete.value) {
    try {
      await deleteBook(bookToDelete.value.id)
      closeDeleteModal()
      await loadBooks() // Перезагружаем книги после удаления
    } catch (err) {
      console.error('Ошибка удаления книги:', err)
      alert('Ошибка удаления книги.')
    }
  }
}

const handleRunImport = async () => {
  try {
    loading.value = true;
    const result = await runImportScript('популярные книги');
    alert(`Скрипт импорта книг успешно запущен. ${result.status || 'Проверьте консоль бэкенда для деталей.'}`);
    await loadBooks(); // Обновляем список книг после импорта
  } catch (err) {
    console.error('Ошибка при запуске скрипта импорта:', err);
    alert('Ошибка при запуске скрипта импорта. Проверьте консоль бэкенда.');
  } finally {
    loading.value = false;
  }
};

// Обработка ошибок загрузки изображений
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  // Предотвращаем бесконечный цикл ошибок
  if (img.src.includes('placeholder-book.svg')) {
    return;
  }
  img.src = '/placeholder-book.svg';
  img.onerror = null; // Убираем обработчик ошибок для заглушки
};

onMounted(() => {
  loadBooks()
})
</script>

<style scoped>
.admin-books {
  padding: 2rem;
  min-height: 100vh;
  background-color: #1a1a1a;
  color: #fff;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #333;
}

.admin-header h2 {
  margin: 0;
  color: #fff;
}

.admin-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #333;
  border-radius: 4px;
  background-color: #2a2a2a;
  color: #fff;
}

.filter-group {
  display: flex;
  gap: 1rem;
}

.filter-group select {
  padding: 0.75rem 1rem;
  border: 1px solid #333;
  border-radius: 4px;
  background-color: #2a2a2a;
  color: #fff;
  min-width: 200px;
}

.admin-table {
  background-color: #2a2a2a;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 2rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #333;
}

th {
  background-color: #333;
  color: #fff;
  font-weight: 500;
}

.book-cover {
  width: 50px;
  height: 75px;
  object-fit: cover;
  border-radius: 4px;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  background-color: #333;
  color: #fff;
}

.btn:hover {
  background-color: #444;
}

.btn-primary {
  background-color: #0d6efd;
}

.btn-primary:hover {
  background-color: #0b5ed7;
}

.btn-secondary {
  background-color: #6c757d;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-edit {
  background-color: #198754;
}

.btn-edit:hover {
  background-color: #157347;
}

.btn-delete {
  background-color: #dc3545;
}

.btn-delete:hover {
  background-color: #bb2d3b;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  background-color: #333;
}

.badge.premium {
  background-color: #ffc107;
  color: #000;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #2a2a2a;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #fff;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #fff;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #333;
  border-radius: 4px;
  background-color: #1a1a1a;
  color: #fff;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-danger {
  background-color: #dc3545;
}

.btn-danger:hover {
  background-color: #bb2d3b;
}

.price-info,
.technical-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

@media (max-width: 768px) {
  .admin-filters {
    flex-direction: column;
  }

  .search-box,
  .filter-group {
    width: 100%;
  }

  .filter-group {
    flex-direction: column;
  }

  .admin-table {
    overflow-x: auto;
  }

  table {
    min-width: 800px;
  }

  .price-info,
  .technical-info {
    grid-template-columns: 1fr;
  }
}
</style>