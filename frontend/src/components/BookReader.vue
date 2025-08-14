<template>
  <div class="book-reader" :class="themeClass">
    <!-- Загрузка -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p class="mt-3">Загрузка содержимого книги...</p>
    </div>
    
    <!-- Ошибка -->
    <div v-else-if="error" class="alert alert-danger text-center">
      <i class="bi bi-exclamation-triangle me-2"></i>
      {{ error }}
    </div>
    
    <!-- Содержимое книги -->
    <div v-else>
      <!-- Информация о прогрессе -->
      <div v-if="progressInfo" class="progress-info mb-3">
        <div class="d-flex justify-content-between align-items-center">
          <span class="text-muted">Страница {{ progressInfo.current_page }} из {{ progressInfo.total_pages }}</span>
          <span class="text-muted">{{ Math.round(progressInfo.progress_percentage) }}% прочитано</span>
        </div>
        <div class="progress mt-2">
          <div class="progress-bar" role="progressbar" 
               :style="{ width: progressInfo.progress_percentage + '%' }"
               :aria-valuenow="progressInfo.progress_percentage" 
               aria-valuemin="0" 
               aria-valuemax="100">
          </div>
        </div>
      </div>

      <!-- Навигация по страницам -->
      <div class="page-navigation mb-4">
        <div class="navigation-container">
          <button 
            class="btn btn-outline-primary nav-btn-left"
            :disabled="!hasPrevious"
            @click="goToPreviousPage"
          >
            <i class="bi bi-chevron-left me-2"></i>
            Предыдущая
          </button>
          
          <div class="page-info page-info-center">
            <span class="fw-bold">{{ currentPage }} / {{ totalPages }}</span>
          </div>
          
          <button 
            class="btn btn-outline-primary nav-btn-right"
            :disabled="!hasNext"
            @click="goToNextPage"
          >
            Следующая
            <i class="bi bi-chevron-right ms-2"></i>
          </button>
        </div>
      </div>

      <!-- Содержимое страницы -->
      <div class="book-content" :class="[fontSizeClass, fontFamilyClass]">
        <div v-if="contentInfo" class="content-info mb-3">
          <i class="fas fa-info-circle"></i> {{ contentInfo }}
        </div>
        <div v-html="renderedContent"></div>
      </div>
      
      <!-- Навигация внизу -->
      <div class="page-navigation mt-4">
        <div class="navigation-container">
          <button 
            class="btn btn-outline-primary nav-btn-left"
            :disabled="!hasPrevious"
            @click="goToPreviousPage"
          >
            <i class="bi bi-chevron-left me-2"></i>
            Предыдущая
          </button>
          
          <div class="page-info page-info-center">
            <span class="fw-bold">{{ currentPage }} / {{ totalPages }}</span>
          </div>
          
          <button 
            class="btn btn-outline-primary nav-btn-right"
            :disabled="!hasNext"
            @click="goToNextPage"
          >
            Следующая
            <i class="bi bi-chevron-right ms-2"></i>
          </button>
        </div>
      </div>
      
      <!-- Кнопка отметки о чтении -->
      <div class="reading-activity-button">
        <button 
          class="btn reading-btn"
          :class="{ 'disabled': !canMarkActivity }"
          :disabled="!canMarkActivity"
          @click="markReadingActivity"
          :title="canMarkActivity ? 'Отметить активность чтения' : `Следующая отметка через ${timeUntilNext}`"
        >
          <i class="bi bi-check-circle-fill me-2"></i>
          <span v-if="canMarkActivity">Читаю</span>
          <span v-else>{{ timeUntilNext }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted, watch } from 'vue';
import { marked } from 'marked';
import { getBookContentPaginated, savePageProgress, getPageProgress, getUserBooks } from '@/api/books';

const props = defineProps<{
  bookId: string;
  fontSize?: 'small' | 'medium' | 'large';
  theme?: 'light' | 'dark' | 'sepia' | 'night' | 'night-sepia' | 'blue';
  fontFamily?: 'serif' | 'sans-serif';
  pageLength?: 'short' | 'medium' | 'long';
}>();

const emit = defineEmits<{
  'update:fontSize': [fontSize: 'small' | 'medium' | 'large'];
  'update:theme': [theme: 'light' | 'dark' | 'sepia' | 'night' | 'night-sepia' | 'blue'];
  'update:fontFamily': [fontFamily: 'serif' | 'sans-serif'];
  'update:pageLength': [pageLength: 'short' | 'medium' | 'long'];
}>();

// Реактивные значения с сохранением в localStorage
const currentFontSize = ref<'small' | 'medium' | 'large'>('medium');
const currentTheme = ref<'light' | 'dark' | 'sepia' | 'night' | 'night-sepia' | 'blue'>('light');
const currentFontFamily = ref<'serif' | 'sans-serif'>('serif');
const currentPageLength = ref<'short' | 'medium' | 'long'>('medium');

const fontSizeClass = computed(() => {
  switch (currentFontSize.value) {
    case 'small': return 'font-small';
    case 'large': return 'font-large';
    default: return 'font-medium';
  }
});

const fontFamilyClass = computed(() => {
  return `font-${currentFontFamily.value}`;
});

const themeClass = computed(() => {
  return `theme-${currentTheme.value}`;
});

// Состояние пагинации
const currentPage = ref(1);
const totalPages = ref(1);
const hasNext = ref(false);
const hasPrevious = ref(false);
const wordsPerPage = computed(() => {
  switch (currentPageLength.value) {
    case 'short': return 200;
    case 'long': return 500;
    default: return 300;
  }
});

// Состояние контента
const renderedContent = ref('');
const contentInfo = ref<string>('');
const isLoading = ref(false);
const error = ref<string | null>(null);
const bookTitle = ref('');
const bookAuthor = ref('');
const userBookId = ref<number | null>(null);
const progressInfo = ref<{
  current_page: number;
  total_pages: number;
  progress_percentage: number;
} | null>(null);

// Логика отметки о чтении с сохранением в localStorage
const lastActivityTime = ref<number | null>(null);
const currentTime = ref(Date.now());
const ACTIVITY_COOLDOWN = 15 * 60 * 1000; // 15 минут в миллисекундах
const readingMarks = ref<number[]>([]); // Массив временных меток отметок чтения

let timeInterval: NodeJS.Timeout | null = null;

// Ключи для localStorage
const STORAGE_KEYS = {
  theme: 'book-reader-theme',
  fontSize: 'book-reader-font-size',
  fontFamily: 'book-reader-font-family',
  pageLength: 'book-reader-page-length',
  lastActivity: `book-reader-last-activity-${props.bookId}`,
  readingMarks: `book-reader-marks-${props.bookId}`,
  currentPage: `book-reader-page-${props.bookId}`
};

// Вычисляемые свойства для отметки о чтении
const canMarkActivity = computed(() => {
  if (!lastActivityTime.value) return true;
  return currentTime.value - lastActivityTime.value >= ACTIVITY_COOLDOWN;
});

const timeUntilNext = computed(() => {
  if (!lastActivityTime.value) return '';
  const timeLeft = ACTIVITY_COOLDOWN - (currentTime.value - lastActivityTime.value);
  if (timeLeft <= 0) return '';
  
  const minutes = Math.ceil(timeLeft / (60 * 1000));
  return `${minutes} мин`;
});

// Функции для работы с localStorage
const saveToStorage = () => {
  localStorage.setItem(STORAGE_KEYS.theme, currentTheme.value);
  localStorage.setItem(STORAGE_KEYS.fontSize, currentFontSize.value);
  localStorage.setItem(STORAGE_KEYS.fontFamily, currentFontFamily.value);
  localStorage.setItem(STORAGE_KEYS.pageLength, currentPageLength.value);
  localStorage.setItem(STORAGE_KEYS.currentPage, currentPage.value.toString());
  if (lastActivityTime.value) {
    localStorage.setItem(STORAGE_KEYS.lastActivity, lastActivityTime.value.toString());
  }
  localStorage.setItem(STORAGE_KEYS.readingMarks, JSON.stringify(readingMarks.value));
};

const loadFromStorage = () => {
  const savedTheme = localStorage.getItem(STORAGE_KEYS.theme);
  const savedFontSize = localStorage.getItem(STORAGE_KEYS.fontSize);
  const savedFontFamily = localStorage.getItem(STORAGE_KEYS.fontFamily);
  const savedPageLength = localStorage.getItem(STORAGE_KEYS.pageLength);
  const savedPage = localStorage.getItem(STORAGE_KEYS.currentPage);
  const savedLastActivity = localStorage.getItem(STORAGE_KEYS.lastActivity);
  const savedReadingMarks = localStorage.getItem(STORAGE_KEYS.readingMarks);
  
  if (savedTheme) {
    currentTheme.value = savedTheme as any;
  }
  if (savedFontSize) {
    currentFontSize.value = savedFontSize as any;
  }
  if (savedFontFamily) {
    currentFontFamily.value = savedFontFamily as any;
  }
  if (savedPageLength) {
    currentPageLength.value = savedPageLength as any;
  }
  if (savedPage) {
    currentPage.value = parseInt(savedPage, 10) || 1;
  }
  if (savedLastActivity) {
    lastActivityTime.value = parseInt(savedLastActivity, 10);
  }
  if (savedReadingMarks) {
    try {
      readingMarks.value = JSON.parse(savedReadingMarks);
    } catch (e) {
      readingMarks.value = [];
    }
  }
};

// Функция обновления текущего времени
const updateCurrentTime = () => {
  currentTime.value = Date.now();
};

// Функция отметки активности чтения
const markReadingActivity = async () => {
  if (!canMarkActivity.value || !userBookId.value) return;
  
  try {
    const now = Date.now();
    lastActivityTime.value = now;
    readingMarks.value.push(now);
    
    // Сохраняем прогресс чтения
    await savePageProgress(Number(props.bookId), currentPage.value, totalPages.value, wordsPerPage.value);
    
    saveToStorage();
    console.log('Активность чтения отмечена');
  } catch (error) {
    console.error('Ошибка при отметке активности чтения:', error);
  }
};

// Функция поиска userBookId
const findUserBookId = async () => {
  try {
    const userBooks = await getUserBooks();
    const userBook = userBooks.find((ub: any) => ub.book.id === Number(props.bookId));
    if (userBook) {
      userBookId.value = userBook.id;
    }
  } catch (error) {
    console.error('Ошибка при поиске userBookId:', error);
  }
};

// Функция загрузки прогресса чтения
const loadProgress = async () => {
  // прогресс по bookId, userBookId не обязателен
  try {
    const progress = await getPageProgress(Number(props.bookId), wordsPerPage.value);
    progressInfo.value = progress;

    // Если есть сохраненный прогресс, переходим на сохраненную страницу
    if (progress.current_page > 0) {
      currentPage.value = progress.current_page;
    }
  } catch (error) {
    console.error('Ошибка при загрузке прогресса:', error);
  }
};

// Функция загрузки содержимого страницы
const fetchPageContent = async () => {
  isLoading.value = true;
  error.value = null;

  try {
    const data = await getBookContentPaginated(
      Number(props.bookId),
      currentPage.value,
      wordsPerPage.value
    );

    console.log('Fetched page data:', {
      title: data.title,
      author: data.author,
      currentPage: data.current_page,
      totalPages: data.total_pages,
      contentLength: data.content.length
    });

    // Обновляем состояние пагинации
    currentPage.value = data.current_page;
    totalPages.value = data.total_pages;
    hasNext.value = data.has_next;
    hasPrevious.value = data.has_previous;

    // Обрабатываем контент
    let processedContent = data.content;

    // Если контент выглядит как Markdown, обрабатываем его
    if (isMarkdownContent(processedContent)) {
      renderedContent.value = await marked(processedContent);
    } else {
      // Иначе отображаем как обычный текст с базовым форматированием
      renderedContent.value = formatPlainText(processedContent);
    }

    bookTitle.value = data.title;
    bookAuthor.value = data.author;

    // Обновляем информацию о прогрессе (без сохранения в базу)
    progressInfo.value = {
      current_page: currentPage.value,
      total_pages: totalPages.value,
      progress_percentage: (currentPage.value / totalPages.value) * 100
    };

    // Сохраняем текущую страницу в localStorage
    saveToStorage();
  } catch (err: any) {
    console.error('Ошибка при загрузке страницы:', err);
    error.value = 'Не удалось загрузить содержимое книги';
  } finally {
    isLoading.value = false;
  }
};

// Функции навигации
const goToNextPage = () => {
  if (hasNext.value) {
    currentPage.value++;
    fetchPageContent();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const goToPreviousPage = () => {
  if (hasPrevious.value) {
    currentPage.value--;
    fetchPageContent();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

// Вспомогательные функции
const isMarkdownContent = (content: string): boolean => {
  return content.includes('#') || content.includes('**') || content.includes('*') || content.includes('[');
};

const formatPlainText = (content: string): string => {
  return content
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0)
    .map(line => `<p>${line}</p>`)
    .join('');
};

// Watchers для синхронизации с родительским компонентом
watch(currentTheme, (newTheme) => {
  saveToStorage();
  emit('update:theme', newTheme);
});

watch(currentFontSize, (newFontSize) => {
  saveToStorage();
  emit('update:fontSize', newFontSize);
});

watch(currentFontFamily, (newFontFamily) => {
  saveToStorage();
  emit('update:fontFamily', newFontFamily);
});

watch(currentPageLength, (newPageLength) => {
  saveToStorage();
  emit('update:pageLength', newPageLength);
  // Перезагружаем контент при изменении длины страницы
  fetchPageContent();
});

// Watchers для props
watch(() => props.theme, (newTheme) => {
  if (newTheme && newTheme !== currentTheme.value) {
    currentTheme.value = newTheme;
  }
});

watch(() => props.fontSize, (newFontSize) => {
  if (newFontSize && newFontSize !== currentFontSize.value) {
    currentFontSize.value = newFontSize;
  }
});

watch(() => props.fontFamily, (newFontFamily) => {
  if (newFontFamily && newFontFamily !== currentFontFamily.value) {
    currentFontFamily.value = newFontFamily;
  }
});

watch(() => props.pageLength, (newPageLength) => {
  if (newPageLength && newPageLength !== currentPageLength.value) {
    currentPageLength.value = newPageLength;
  }
});

// Обработка клавиш для навигации
const handleKeyPress = (event: KeyboardEvent) => {
  if (event.key === 'ArrowLeft' && hasPrevious.value) {
    goToPreviousPage();
  } else if (event.key === 'ArrowRight' && hasNext.value) {
    goToNextPage();
  }
};

onMounted(async () => {
  loadFromStorage();
  await findUserBookId();
  await loadProgress();
  await fetchPageContent();
  
  // Обновляем время каждую секунду для корректного отображения таймера
  timeInterval = setInterval(updateCurrentTime, 1000);
  
  // Добавляем обработчик клавиш
  window.addEventListener('keydown', handleKeyPress);
});

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval);
  }
  window.removeEventListener('keydown', handleKeyPress);
  saveToStorage();
});
</script>

<style scoped>
.book-reader {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  transition: all 0.3s ease;
}

/* Тематические стили для общего фона читалки */

/* Светлая тема */
.theme-light {
  background: #f8f9fa !important;
  color: #212529 !important;
}

/* Темная тема */
.theme-dark {
  background: #212529 !important;
  color: #f8f9fa !important;
}

/* Сепия тема */
.theme-sepia {
  background: #f5f5dc !important;
  color: #8b4513 !important;
}

/* Ночная тема */
.theme-night {
  background: #0f0f23 !important;
  color: #e9ecef !important;
}

/* Ночная сепия тема */
.theme-night-sepia {
  background: #1a1611 !important;
  color: #f5f5dc !important;
}

/* Синяя тема */
.theme-blue {
  background: #e6f3ff !important;
  color: #1e3a5f !important;
}

.book-content {
  background: #fff;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  line-height: 1.8;
  font-family: 'Georgia', 'Times New Roman', serif;
  transition: all 0.3s ease;
  margin-bottom: 30px;
  color: #2c3e50;
}

/* Тематические стили для контента книги */

/* Светлая тема */
.theme-light .book-content {
  background: #fff !important;
  color: #2c3e50 !important;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
}

/* Темная тема */
.theme-dark .book-content {
  background: #2c3e50 !important;
  color: #ecf0f1 !important;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
}

/* Сепия тема */
.theme-sepia .book-content {
  background: #f4f1e8 !important;
  color: #5d4e37 !important;
  box-shadow: 0 4px 6px rgba(93, 78, 55, 0.2) !important;
}

/* Ночная тема */
.theme-night .book-content {
  background: #1a1a2e !important;
  color: #c9c9c9 !important;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5) !important;
}

/* Ночная сепия тема */
.theme-night-sepia .book-content {
  background: #2d2a24 !important;
  color: #d4c5a9 !important;
  box-shadow: 0 4px 6px rgba(45, 42, 36, 0.5) !important;
}

/* Синяя тема */
.theme-blue .book-content {
  background: #f0f4f8 !important;
  color: #1e3a5f !important;
  box-shadow: 0 4px 6px rgba(30, 58, 95, 0.2) !important;
}

/* Общие стили для блока прогресса */
.progress-info {
  background: rgba(255, 255, 255, 0.9);
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease, color 0.3s ease, box-shadow 0.3s ease;
}

.progress-info .text-muted {
  color: #6c757d !important;
}

.progress-info .progress {
  height: 8px;
  border-radius: 6px;
  background-color: #e9ecef;
}

.progress-info .progress-bar {
  border-radius: 6px;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  transition: width 0.3s ease, background-color 0.3s ease, background 0.3s ease;
}

/* Тематические стили для блока прогресса */

/* Светлая тема */
.theme-light .progress-info {
  background: rgba(255, 255, 255, 0.95) !important;
  color: #212529 !important;
}
.theme-light .progress-info .text-muted {
  color: #6c757d !important;
}
.theme-light .progress-info .progress {
  background-color: #e9ecef !important;
}
.theme-light .progress-info .progress-bar {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%) !important;
}

/* Темная тема */
.theme-dark .progress-info {
  background: rgba(52, 58, 64, 0.9) !important;
  color: #f8f9fa !important;
}
.theme-dark .progress-info .text-muted {
  color: #adb5bd !important;
}
.theme-dark .progress-info .progress {
  background-color: #495057 !important;
}
.theme-dark .progress-info .progress-bar {
  background: linear-gradient(135deg, #0d6efd 0%, #084298 100%) !important;
}

/* Сепия тема */
.theme-sepia .progress-info {
  background: rgba(245, 245, 220, 0.9) !important;
  color: #8b4513 !important;
}
.theme-sepia .progress-info .text-muted {
  color: #a0522d !important;
}
.theme-sepia .progress-info .progress {
  background-color: #deb887 !important;
}
.theme-sepia .progress-info .progress-bar {
  background: linear-gradient(135deg, #cd853f 0%, #8b4513 100%) !important;
}

/* Ночная тема */
.theme-night .progress-info {
  background: rgba(33, 37, 41, 0.9) !important;
  color: #e9ecef !important;
}
.theme-night .progress-info .text-muted {
  color: #6c757d !important;
}
.theme-night .progress-info .progress {
  background-color: #495057 !important;
}
.theme-night .progress-info .progress-bar {
  background: linear-gradient(135deg, #198754 0%, #146c43 100%) !important;
}

/* Ночная сепия тема */
.theme-night-sepia .progress-info {
  background: rgba(139, 69, 19, 0.9) !important;
  color: #f5f5dc !important;
}
.theme-night-sepia .progress-info .text-muted {
  color: #deb887 !important;
}
.theme-night-sepia .progress-info .progress {
  background-color: #a0522d !important;
}
.theme-night-sepia .progress-info .progress-bar {
  background: linear-gradient(135deg, #cd853f 0%, #a0522d 100%) !important;
}

/* Синяя тема */
.theme-blue .progress-info {
  background: rgba(240, 244, 248, 0.9) !important;
  color: #1e3a5f !important;
}
.theme-blue .progress-info .text-muted {
  color: #44638a !important;
}
.theme-blue .progress-info .progress {
  background-color: #e2e8f0 !important;
}
.theme-blue .progress-info .progress-bar {
  background: linear-gradient(135deg, var(--primary-color) 0%, #7fb069 100%) !important;
}

.page-navigation {
  padding: 20px 0;
}

.navigation-container {
  display: flex;
  align-items: center;
  position: relative;
  width: 100%;
}

.nav-btn-left {
  position: absolute;
  left: 0;
}

.nav-btn-right {
  position: absolute;
  right: 0;
}

.page-navigation .btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #ffffff;
  padding: 12px 24px;
  border-radius: 25px;
  font-weight: 600;
  font-size: 0.95rem;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  display: flex;
  align-items: center;
  min-width: 140px;
  justify-content: center;
}

/* Тематические стили для кнопок навигации */

/* Светлая тема */
.theme-light .page-navigation .btn {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%) !important;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3) !important;
}

.theme-light .page-navigation .btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #0056b3 0%, #007bff 100%) !important;
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4) !important;
}

/* Темная тема */
.theme-dark .page-navigation .btn {
  background: linear-gradient(135deg, #495057 0%, #343a40 100%) !important;
  box-shadow: 0 4px 15px rgba(73, 80, 87, 0.3) !important;
}

.theme-dark .page-navigation .btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #343a40 0%, #495057 100%) !important;
  box-shadow: 0 6px 20px rgba(73, 80, 87, 0.4) !important;
}

/* Сепия тема */
.theme-sepia .page-navigation .btn {
  background: linear-gradient(135deg, #cd853f 0%, #8b4513 100%) !important;
  box-shadow: 0 4px 15px rgba(205, 133, 63, 0.3) !important;
}

.theme-sepia .page-navigation .btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #8b4513 0%, #cd853f 100%) !important;
  box-shadow: 0 6px 20px rgba(205, 133, 63, 0.4) !important;
}

/* Ночная тема */
.theme-night .page-navigation .btn {
  background: linear-gradient(135deg, #198754 0%, #146c43 100%) !important;
  box-shadow: 0 4px 15px rgba(25, 135, 84, 0.3) !important;
}

.theme-night .page-navigation .btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #146c43 0%, #198754 100%) !important;
  box-shadow: 0 6px 20px rgba(25, 135, 84, 0.4) !important;
}

/* Ночная сепия тема */
.theme-night-sepia .page-navigation .btn {
  background: linear-gradient(135deg, #cd853f 0%, #a0522d 100%) !important;
  color: #f5deb3 !important;
  box-shadow: 0 4px 15px rgba(205, 133, 63, 0.4) !important;
}

.theme-night-sepia .page-navigation .btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #a0522d 0%, #cd853f 100%) !important;
  box-shadow: 0 6px 20px rgba(205, 133, 63, 0.5) !important;
}

/* Синяя тема */
.theme-blue .page-navigation .btn {
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%) !important;
  box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3) !important;
}

.theme-blue .page-navigation .btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #357abd 0%, #4a90e2 100%) !important;
  box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4) !important;
}

.page-navigation .btn:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.page-navigation .btn:disabled {
  background: linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%);
  color: #7f8c8d;
  cursor: not-allowed;
  box-shadow: 0 2px 8px rgba(189, 195, 199, 0.2);
  transform: none;
}

.page-info {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 12px 20px;
  border-radius: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  font-weight: 600;
  color: #495057;
  border: 2px solid rgba(102, 126, 234, 0.2);
  min-width: 100px;
  text-align: center;
}

/* Тематические стили для информации о странице */

/* Светлая тема */
.theme-light .page-info {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
  color: #495057 !important;
  border: 2px solid rgba(0, 123, 255, 0.2) !important;
}

/* Темная тема */
.theme-dark .page-info {
  background: linear-gradient(135deg, #495057 0%, #343a40 100%) !important;
  color: #f8f9fa !important;
  border: 2px solid rgba(73, 80, 87, 0.3) !important;
}

/* Сепия тема */
.theme-sepia .page-info {
  background: linear-gradient(135deg, #f4f1e8 0%, #e8e2d5 100%) !important;
  color: #5d4e37 !important;
  border: 2px solid rgba(205, 133, 63, 0.3) !important;
}

/* Ночная тема */
.theme-night .page-info {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
  color: #c9c9c9 !important;
  border: 2px solid rgba(25, 135, 84, 0.3) !important;
}

/* Ночная сепия тема */
.theme-night-sepia .page-info {
  background: linear-gradient(135deg, #3a3530 0%, #4a453e 100%) !important;
  color: #f5deb3 !important;
  border: 2px solid rgba(205, 133, 63, 0.4) !important;
}

/* Синяя тема */
.theme-blue .page-info {
  background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%) !important;
  color: #1e3a5f !important;
  border: 2px solid rgba(74, 144, 226, 0.3) !important;
}

.page-info-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.content-info {
  background: #e3f2fd;
  color: #1976d2;
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 4px solid #1976d2;
  font-size: 0.9rem;
}

.book-content :deep(h1) {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 0.5rem;
}

.book-content :deep(h2) {
  font-size: 1.5rem;
  margin: 2rem 0 1rem 0;
  color: #34495e;
}

.book-content :deep(h3) {
  font-size: 1.3rem;
  margin: 1.5rem 0 1rem 0;
  color: #34495e;
}

.book-content :deep(p) {
  margin-bottom: 1.2rem;
  text-align: justify;
  text-indent: 2em;
}

.book-content :deep(strong) {
  font-weight: 600;
  color: #2c3e50;
}

.book-content :deep(em) {
  font-style: italic;
  color: #7f8c8d;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
  border: 0.3em solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spinner-border 0.75s linear infinite;
}

@keyframes spinner-border {
  to {
    transform: rotate(360deg);
  }
}

.spinner-border.text-primary {
  color: currentColor;
}

/* Размеры шрифта */
.font-small {
  font-size: 0.9rem;
}

.font-medium {
  font-size: 1rem;
}

.font-large {
  font-size: 1.2rem;
}

/* Семейства шрифтов */
.font-serif {
  font-family: 'Georgia', 'Times New Roman', serif;
}

.font-sans-serif {
  font-family: 'Helvetica', 'Arial', sans-serif;
}

/* Кнопка отметки о чтении */
.reading-activity-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.reading-btn {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  border: none;
  color: white;
  padding: 12px 20px;
  border-radius: 25px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
  transition: all 0.3s ease;
  min-width: 120px;
}

.reading-btn:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
  background: linear-gradient(135deg, #20c997 0%, #28a745 100%);
}

.reading-btn.disabled {
  background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
  cursor: not-allowed;
  opacity: 0.7;
}

/* Тематические стили для кнопки "Читаю" */

/* Светлая тема */
.theme-light .reading-btn {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%) !important;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3) !important;
}

.theme-light .reading-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #0056b3 0%, #007bff 100%) !important;
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4) !important;
}

/* Темная тема */
.theme-dark .reading-btn {
  background: linear-gradient(135deg, #495057 0%, #343a40 100%) !important;
  box-shadow: 0 4px 15px rgba(73, 80, 87, 0.3) !important;
}

.theme-dark .reading-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #343a40 0%, #495057 100%) !important;
  box-shadow: 0 6px 20px rgba(73, 80, 87, 0.4) !important;
}

/* Сепия тема */
.theme-sepia .reading-btn {
  background: linear-gradient(135deg, #cd853f 0%, #8b4513 100%) !important;
  box-shadow: 0 4px 15px rgba(205, 133, 63, 0.3) !important;
}

.theme-sepia .reading-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #8b4513 0%, #cd853f 100%) !important;
  box-shadow: 0 6px 20px rgba(205, 133, 63, 0.4) !important;
}

/* Ночная тема */
.theme-night .reading-btn {
  background: linear-gradient(135deg, #198754 0%, #146c43 100%) !important;
  box-shadow: 0 4px 15px rgba(25, 135, 84, 0.3) !important;
}

.theme-night .reading-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #146c43 0%, #198754 100%) !important;
  box-shadow: 0 6px 20px rgba(25, 135, 84, 0.4) !important;
}

/* Ночная сепия тема */
.theme-night-sepia .reading-btn {
  background: linear-gradient(135deg, #cd853f 0%, #a0522d 100%) !important;
  color: #f5deb3 !important;
  box-shadow: 0 4px 15px rgba(205, 133, 63, 0.4) !important;
}

.theme-night-sepia .reading-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #a0522d 0%, #cd853f 100%) !important;
  box-shadow: 0 6px 20px rgba(205, 133, 63, 0.5) !important;
}

/* Синяя тема */
.theme-blue .reading-btn {
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%) !important;
  box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3) !important;
}

.theme-blue .reading-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #357abd 0%, #4a90e2 100%) !important;
  box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4) !important;
}

/* Адаптивность */
@media (max-width: 768px) {
  .book-reader {
    padding: 10px;
  }
  
  .book-content {
    padding: 20px;
  }
  
  .page-navigation .btn {
    padding: 10px 16px;
    font-size: 0.9rem;
    min-width: 120px;
  }
  
  .page-info {
    padding: 10px 16px;
    font-size: 0.9rem;
  }
  
  .reading-activity-button {
    bottom: 15px;
    right: 15px;
  }
  
  .reading-btn {
    padding: 10px 16px;
    font-size: 0.9rem;
    min-width: 100px;
  }
}
</style>