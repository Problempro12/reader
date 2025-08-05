<template>
  <div class="book-reader-page" :class="`theme-${currentTheme}`">
    <!-- Навигация -->
    <nav class="reader-nav mb-4">
      <div class="container-fluid">
        <div class="d-flex align-items-center justify-content-between nav-content">
          <div class="d-flex align-items-center">
            <RouterLink :to="`/books/${bookId}`" class="btn btn-outline-secondary me-3">
              <i class="bi bi-arrow-left me-2"></i>
              Назад к книге
            </RouterLink>
            <div v-if="bookInfo" class="book-info">
              <h5 class="mb-0 text-truncate">{{ bookInfo.title }}</h5>
              <small>{{ bookInfo.author }}</small>
            </div>
          </div>
          <div class="reader-controls">
            <button class="btn btn-outline-primary" @click="showSettings = true">
              <i class="bi bi-gear"></i>
            </button>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Компонент читалки -->
    <div class="container-fluid">
      <BookReader :book-id="bookId" :font-size="fontSize" :theme="currentTheme" />
    </div>

    <!-- Модальное окно настроек -->
    <div v-if="showSettings" class="modal-overlay" @click="showSettings = false">
      <div class="settings-modal" @click.stop>
        <div class="modal-header">
          <h5 class="modal-title">Настройки читалки</h5>
          <button type="button" class="btn-close" @click="showSettings = false">
            <i class="bi bi-x"></i>
          </button>
        </div>
        <div class="modal-body">
          <!-- Размер шрифта -->
          <div class="setting-group">
            <label class="setting-label">Размер шрифта</label>
            <div class="font-size-options">
              <button 
                v-for="size in ['small', 'medium', 'large']" 
                :key="size"
                class="btn font-size-btn"
                :class="{ 'active': fontSize === size }"
                @click="fontSize = size as 'small' | 'medium' | 'large'"
              >
                {{ size === 'small' ? 'Маленький' : size === 'medium' ? 'Средний' : 'Большой' }}
              </button>
            </div>
          </div>
          
          <!-- Тема -->
          <div class="setting-group">
            <label class="setting-label">Тема</label>
            <div class="theme-options">
              <button 
                v-for="theme in themes" 
                :key="theme.id"
                class="btn theme-btn"
                :class="[`theme-preview-${theme.id}`, { 'active': currentTheme === theme.id }]"
                @click="currentTheme = theme.id as 'light' | 'dark' | 'sepia' | 'night' | 'night-sepia' | 'blue'"
              >
                <div class="theme-preview">
                  <div class="preview-header"></div>
                  <div class="preview-content">
                    <div class="preview-text"></div>
                    <div class="preview-text short"></div>
                  </div>
                </div>
                <span class="theme-name">
                  <i :class="theme.icon" class="me-2"></i>
                  {{ theme.name }}
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import BookReader from '@/components/BookReader.vue';
import { getBookContent } from '@/api/books';

const route = useRoute();
const bookId = route.params.id as string;

const bookInfo = ref<{ title: string; author: string } | null>(null);
const fontSize = ref<'small' | 'medium' | 'large'>('medium');
const currentTheme = ref<'light' | 'dark' | 'sepia' | 'night' | 'night-sepia' | 'blue'>('light');
const showSettings = ref(false);

// Ключи для localStorage
const STORAGE_KEYS = {
  theme: 'book-reader-theme',
  fontSize: 'book-reader-font-size'
};

// Функции для работы с localStorage
const loadFromStorage = () => {
  // Загружаем тему
  const savedTheme = localStorage.getItem(STORAGE_KEYS.theme);
  if (savedTheme && ['light', 'dark', 'sepia', 'night', 'night-sepia', 'blue'].includes(savedTheme)) {
    currentTheme.value = savedTheme as any;
  }
  
  // Загружаем размер шрифта
  const savedFontSize = localStorage.getItem(STORAGE_KEYS.fontSize);
  if (savedFontSize && ['small', 'medium', 'large'].includes(savedFontSize)) {
    fontSize.value = savedFontSize as any;
  }
};

const saveToStorage = () => {
  localStorage.setItem(STORAGE_KEYS.theme, currentTheme.value);
  localStorage.setItem(STORAGE_KEYS.fontSize, fontSize.value);
};

const themes = [
  { id: 'light', name: 'Светлая', icon: 'bi bi-sun' },
  { id: 'sepia', name: 'Сепия', icon: 'bi bi-book' },
  { id: 'blue', name: 'Синяя', icon: 'bi bi-droplet' },
  { id: 'dark', name: 'Темная', icon: 'bi bi-moon' },
  { id: 'night', name: 'Ночная', icon: 'bi bi-moon-stars' },
  { id: 'night-sepia', name: 'Ночная сепия', icon: 'bi bi-moon-fill' }
];

const fetchBookInfo = async () => {
  try {
    const data = await getBookContent(Number(bookId));
    bookInfo.value = {
      title: data.title,
      author: data.author
    };
  } catch (error) {
    console.error('Ошибка при загрузке информации о книге:', error);
  }
};

// Watchers для сохранения изменений
watch(currentTheme, () => {
  saveToStorage();
});

watch(fontSize, () => {
  saveToStorage();
});

onMounted(() => {
  loadFromStorage();
  fetchBookInfo();
});

// Настройки теперь управляются через модальное окно
</script>

<style scoped>
/* Базовые стили */
.book-reader-page {
  min-height: 100vh;
  transition: all 0.3s ease;
}

.reader-nav {
  padding: 15px 0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 0 0 20px 20px;
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  animation: slideDown 0.6s ease-out;
}

@keyframes slideDown {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.nav-content {
  padding: 0 20px;
  min-height: 60px;
  align-items: center;
}

/* Светлая тема */
.theme-light {
  background-color: #f8f9fa;
}

.theme-light .reader-nav {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  box-shadow: 0 4px 15px rgba(44, 62, 80, 0.3);
}

/* Темная тема */
.theme-dark {
  background-color: #1a1a2e;
}

.theme-dark .reader-nav {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
}

/* Сепия тема */
.theme-sepia {
  background-color: #f4f1e8;
}

.theme-sepia .reader-nav {
  background: linear-gradient(135deg, #d4a574 0%, #c19a6b 100%);
}

/* Ночная тема */
.theme-night {
  background-color: #0f0f23;
}

.theme-night .reader-nav {
  background: linear-gradient(135deg, #1a1a3a 0%, #2d2d5f 100%);
}

/* Ночная сепия тема */
.theme-night-sepia {
  background-color: #1a1612;
}

.theme-night-sepia .reader-nav {
  background: linear-gradient(135deg, #3d2f1f 0%, #4a3426 100%);
}

/* Синяя тема */
.theme-blue {
  background-color: #e8f4fd;
}

.theme-blue .reader-nav {
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
}

.reader-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.reader-controls .btn {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: white;
  backdrop-filter: blur(15px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 12px;
  padding: 10px 16px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.reader-controls .btn:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  color: white;
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.btn-outline-secondary {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: white;
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-outline-secondary:hover {
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.4);
  color: white;
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.book-info {
  max-width: 400px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.book-info:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.book-info h5 {
  color: white;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  font-size: 1.1rem;
  letter-spacing: 0.3px;
  margin-bottom: 2px;
}

.book-info small {
  color: rgba(255, 255, 255, 0.85);
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  font-weight: 400;
  font-size: 0.9rem;
  letter-spacing: 0.2px;
}

/* Цвета текста для тем */
.theme-light .book-info h5,
.theme-light .book-info small {
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
}

.theme-dark .book-info h5,
.theme-dark .book-info small {
  color: #ecf0f1;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
}

.theme-sepia .book-info h5,
.theme-sepia .book-info small {
  color: #2c3e50;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.5);
}

.theme-night .book-info h5,
.theme-night .book-info small {
  color: #b8c5d6;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
}

.theme-night-sepia .book-info h5,
.theme-night-sepia .book-info small {
  color: #d4a574;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
}

.theme-blue .book-info h5,
.theme-blue .book-info small {
  color: #1e3a5f;
  text-shadow: 0 1px 3px rgba(255, 255, 255, 0.5);
}

/* Модальное окно настроек */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

/* Фон модального окна для разных тем */
.theme-light .modal-overlay {
  background: rgba(248, 249, 250, 0.8);
}

.theme-dark .modal-overlay {
  background: rgba(26, 26, 46, 0.8);
}

.theme-sepia .modal-overlay {
  background: rgba(244, 241, 232, 0.8);
}

.theme-night .modal-overlay {
  background: rgba(15, 15, 35, 0.8);
}

.theme-night-sepia .modal-overlay {
  background: rgba(26, 22, 18, 0.8);
}

.theme-blue .modal-overlay {
  background: rgba(232, 244, 253, 0.8);
}

.settings-modal {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  max-width: 400px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #a8e6cf 0%, #8cd3b0 100%);
  color: #2c3e50;
}

/* Заголовки модального окна для разных тем */
.theme-dark .modal-header {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: #ecf0f1;
  border-bottom-color: #34495e;
}

.theme-night .modal-header {
  background: linear-gradient(135deg, #1a1a3a 0%, #2d2d5f 100%);
  color: #b8c5d6;
  border-bottom-color: #2d2d5f;
}

.theme-sepia .modal-header {
  background: linear-gradient(135deg, #d4a574 0%, #c19a6b 100%);
  color: #5d4e37;
  border-bottom-color: #c19a6b;
}

.theme-night-sepia .modal-header {
  background: linear-gradient(135deg, #3d2f1f 0%, #4a3426 100%);
  color: #d4a574;
  border-bottom-color: #4a3426;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.btn-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Кнопка закрытия для разных тем */
.theme-dark .btn-close,
.theme-night .btn-close {
  color: #ecf0f1;
}

.theme-dark .btn-close:hover,
.theme-night .btn-close:hover {
  background: rgba(236, 240, 241, 0.2);
}

.theme-sepia .btn-close {
  color: #5d4e37;
}

.theme-sepia .btn-close:hover {
  background: rgba(93, 78, 55, 0.2);
}

.theme-night-sepia .btn-close {
  color: #d4a574;
}

.theme-night-sepia .btn-close:hover {
  background: rgba(212, 165, 116, 0.2);
}

.modal-body {
  padding: 24px;
}

.setting-group {
  margin-bottom: 24px;
}

.setting-group:last-child {
  margin-bottom: 0;
}

.setting-label {
  display: block;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 12px;
  font-size: 0.95rem;
}

.font-size-options {
  display: flex;
  gap: 8px;
}

.font-size-btn {
  flex: 1;
  padding: 10px 16px;
  border: 2px solid #e9ecef;
  background: #f8f9fa;
  color: #6c757d;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}

.font-size-btn:hover {
  border-color: #a8e6cf;
  color: #a8e6cf;
}

.font-size-btn.active {
  background: #a8e6cf;
  border-color: #a8e6cf;
  color: #2c3e50;
}

.theme-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  justify-content: center;
}

@media (min-width: 768px) {
  .theme-options {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1024px) {
  .theme-options {
    grid-template-columns: repeat(3, 1fr);
  }
}

.theme-btn {
  padding: 16px 12px;
  border: 2px solid #e9ecef;
  background: #f8f9fa;
  color: #6c757d;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.3s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
}

.theme-btn:hover {
  border-color: #a8e6cf;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(168, 230, 207, 0.2);
}

.theme-btn.active {
  background: #a8e6cf;
  border-color: #a8e6cf;
  color: #2c3e50;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(168, 230, 207, 0.3);
}

.theme-preview {
  width: 40px;
  height: 30px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.1);
  position: relative;
}

.preview-header {
  height: 8px;
  width: 100%;
}

.preview-content {
  padding: 4px;
  height: 22px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.preview-text {
  height: 2px;
  border-radius: 1px;
  opacity: 0.7;
}

.preview-text.short {
  width: 60%;
}

.theme-name {
  font-size: 0.8rem;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Превью для светлой темы */
.theme-preview-light .preview-header {
  background: linear-gradient(135deg, #a8e6cf 0%, #8cd3b0 100%);
}

.theme-preview-light .preview-content {
  background: #f8f9fa;
}

.theme-preview-light .preview-text {
  background: #2c3e50;
}

/* Превью для темной темы */
.theme-preview-dark .preview-header {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
}

.theme-preview-dark .preview-content {
  background: #1a1a2e;
}

.theme-preview-dark .preview-text {
  background: #ecf0f1;
}

/* Превью для сепия темы */
.theme-preview-sepia .preview-header {
  background: linear-gradient(135deg, #d4a574 0%, #c19a6b 100%);
}

.theme-preview-sepia .preview-content {
  background: #f4f1e8;
}

.theme-preview-sepia .preview-text {
  background: #5d4e37;
}

/* Превью для ночной темы */
.theme-preview-night .preview-header {
  background: linear-gradient(135deg, #1a1a3a 0%, #2d2d5f 100%);
}

.theme-preview-night .preview-content {
  background: #0f0f23;
}

.theme-preview-night .preview-text {
  background: #b8c5d6;
}

/* Превью для ночной сепия темы */
.theme-preview-night-sepia .preview-header {
  background: linear-gradient(135deg, #3d2f1f 0%, #4a3426 100%);
}

.theme-preview-night-sepia .preview-content {
  background: #1a1612;
}

.theme-preview-night-sepia .preview-text {
  background: #d4a574;
}

/* Превью для синей темы */
.theme-preview-blue .preview-header {
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
}

.theme-preview-blue .preview-content {
  background: #e8f4fd;
}

.theme-preview-blue .preview-text {
  background: #2c3e50;
}

/* Темные темы для модального окна */
.theme-dark .settings-modal,
.theme-night .settings-modal {
  background: #2c3e50;
  color: #ecf0f1;
}

.theme-dark .modal-header,
.theme-night .modal-header {
  border-bottom-color: #34495e;
}

.theme-dark .setting-label,
.theme-night .setting-label {
  color: #ecf0f1;
}

.theme-dark .font-size-btn,
.theme-dark .theme-btn,
.theme-night .font-size-btn,
.theme-night .theme-btn {
  background: #34495e;
  border-color: #4a5f7a;
  color: #bdc3c7;
}

.theme-dark .font-size-btn:hover,
.theme-dark .theme-btn:hover,
.theme-night .font-size-btn:hover,
.theme-night .theme-btn:hover {
  border-color: #a8e6cf;
  color: #a8e6cf;
}

/* Ночная сепия тема для модального окна */
.theme-night-sepia .settings-modal {
  background: #2a1f15;
  color: #d4a574;
}

.theme-night-sepia .modal-header {
  border-bottom-color: #3d2f1f;
}

.theme-night-sepia .setting-label {
  color: #d4a574;
}

.theme-night-sepia .font-size-btn,
.theme-night-sepia .theme-btn {
  background: #3d2f1f;
  border-color: #4a3426;
  color: #c19a6b;
}

.theme-night-sepia .font-size-btn:hover,
.theme-night-sepia .theme-btn:hover {
  border-color: #d4a574;
  color: #d4a574;
}

/* Сепия тема для модального окна */
.theme-sepia .settings-modal {
  background: #f4f1e8;
  color: #5d4e37;
}

.theme-sepia .modal-header {
  border-bottom-color: #e6dcc6;
}

.theme-sepia .setting-label {
  color: #5d4e37;
}

.theme-sepia .font-size-btn,
.theme-sepia .theme-btn {
  background: #ede8dc;
  border-color: #d4c4a8;
  color: #8b7355;
}

.theme-sepia .font-size-btn:hover,
.theme-sepia .theme-btn:hover {
  border-color: #d4a574;
  color: #d4a574;
}

@media (max-width: 768px) {
  .reader-nav {
    padding: 10px 0;
  }
  
  .reader-controls {
    gap: 5px;
  }
  
  .book-info {
    max-width: 200px;
  }
  
  .book-info h5 {
    font-size: 1rem;
  }
  
  .settings-modal {
    width: 95%;
    margin: 20px;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .theme-btn {
    padding: 12px;
  }
  
  .theme-preview {
    width: 35px;
    height: 25px;
  }
}
</style>