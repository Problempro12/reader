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
      <div class="book-content" :class="[fontSizeClass]">
        <div v-if="contentInfo" class="content-info">
          <i class="fas fa-info-circle"></i> {{ contentInfo }}
        </div>
        <div v-html="renderedContent"></div>
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
import { getBookContent, addReadingProgress, getUserBooks } from '@/api/books';
import JSZip from 'jszip';

const props = defineProps<{
  bookId: string;
  fontSize?: 'small' | 'medium' | 'large';
  theme?: 'light' | 'dark' | 'sepia' | 'night' | 'night-sepia' | 'blue';
}>();

const emit = defineEmits<{
  'update:fontSize': [fontSize: 'small' | 'medium' | 'large'];
  'update:theme': [theme: 'light' | 'dark' | 'sepia' | 'night' | 'night-sepia' | 'blue'];
}>();

// Реактивные значения с сохранением в localStorage
const currentFontSize = ref<'small' | 'medium' | 'large'>('medium');
const currentTheme = ref<'light' | 'dark' | 'sepia' | 'night' | 'night-sepia' | 'blue'>('light');

const fontSizeClass = computed(() => {
  switch (currentFontSize.value) {
    case 'small': return 'font-small';
    case 'large': return 'font-large';
    default: return 'font-medium';
  }
});

const themeClass = computed(() => {
  return `theme-${currentTheme.value}`;
});

const renderedContent = ref('');
const contentInfo = ref<string>('');
const isLoading = ref(false);
const error = ref<string | null>(null);
const bookTitle = ref('');
const bookAuthor = ref('');
const userBookId = ref<number | null>(null);

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
  lastActivity: `book-reader-last-activity-${props.bookId}`,
  readingMarks: `book-reader-marks-${props.bookId}`
};

const canMarkActivity = computed(() => {
  if (!lastActivityTime.value) return true;
  return currentTime.value - lastActivityTime.value >= ACTIVITY_COOLDOWN;
});

const timeUntilNext = computed(() => {
  if (!lastActivityTime.value || canMarkActivity.value) return '';
  
  const timeLeft = ACTIVITY_COOLDOWN - (currentTime.value - lastActivityTime.value);
  const minutes = Math.floor(timeLeft / (60 * 1000));
  const seconds = Math.floor((timeLeft % (60 * 1000)) / 1000);
  
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
});

// Функции для работы с localStorage
const loadFromStorage = () => {
  // Загружаем тему
  const savedTheme = localStorage.getItem(STORAGE_KEYS.theme);
  if (savedTheme && ['light', 'dark', 'sepia', 'night', 'night-sepia', 'blue'].includes(savedTheme)) {
    currentTheme.value = savedTheme as any;
  } else if (props.theme) {
    currentTheme.value = props.theme;
  }
  
  // Загружаем размер шрифта
  const savedFontSize = localStorage.getItem(STORAGE_KEYS.fontSize);
  if (savedFontSize && ['small', 'medium', 'large'].includes(savedFontSize)) {
    currentFontSize.value = savedFontSize as any;
  } else if (props.fontSize) {
    currentFontSize.value = props.fontSize;
  }
  
  // Загружаем время последней активности
  const savedLastActivity = localStorage.getItem(STORAGE_KEYS.lastActivity);
  if (savedLastActivity) {
    lastActivityTime.value = parseInt(savedLastActivity);
  }
  
  // Загружаем отметки чтения
  const savedMarks = localStorage.getItem(STORAGE_KEYS.readingMarks);
  if (savedMarks) {
    try {
      readingMarks.value = JSON.parse(savedMarks);
    } catch (e) {
      readingMarks.value = [];
    }
  }
};

const saveToStorage = () => {
  localStorage.setItem(STORAGE_KEYS.theme, currentTheme.value);
  localStorage.setItem(STORAGE_KEYS.fontSize, currentFontSize.value);
  if (lastActivityTime.value) {
    localStorage.setItem(STORAGE_KEYS.lastActivity, lastActivityTime.value.toString());
  }
  localStorage.setItem(STORAGE_KEYS.readingMarks, JSON.stringify(readingMarks.value));
};

// Функция для получения userBookId
const findUserBookId = async () => {
  try {
    const userBooks = await getUserBooks();
    const userBook = userBooks.find(ub => ub.book.id === Number(props.bookId));
    if (userBook) {
      userBookId.value = userBook.id;
    }
  } catch (err) {
    console.error('Ошибка при получении userBookId:', err);
  }
};

const markReadingActivity = async () => {
  if (!canMarkActivity.value) return;
  
  const now = Date.now();
  lastActivityTime.value = now;
  currentTime.value = now;
  
  // Добавляем отметку в локальный массив
  readingMarks.value.push(now);
  
  // Сохраняем в localStorage
  saveToStorage();
  
  // Отправляем на сервер
  if (userBookId.value) {
    try {
      await addReadingProgress(userBookId.value, Math.floor(Math.random() * 1000)); // Позиция - заглушка
      console.log('Отметка о чтении отправлена на сервер:', new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Ошибка при отправке отметки на сервер:', err);
    }
  }
  
  console.log('Отметка о чтении зафиксирована:', new Date().toLocaleTimeString());
  console.log('Всего отметок:', readingMarks.value.length, 'Часов чтения:', Math.floor(readingMarks.value.length / 4));
};

const updateCurrentTime = () => {
  currentTime.value = Date.now();
};

// Вспомогательные функции для обработки контента
const isBase64Archive = (content: string): boolean => {
  try {
    console.log('isBase64Archive called with content length:', content.length);
    
    // Проверяем, начинается ли контент с base64 символов
    if (!content || content.length < 10) {
      console.log('Content too short:', content.length);
      return false;
    }
    
    console.log('Content start (first 50 chars):', content.substring(0, 50));
    
    // Проверяем, является ли строка валидным base64
    const testString = content.substring(0, 100);
    console.log('Testing base64 decode with first 100 chars:', testString);
    
    const decoded = atob(testString);
    console.log('Base64 decoded successfully, length:', decoded.length);
    
    // Проверяем сигнатуру ZIP-файла (PK)
    const byte0 = decoded.charCodeAt(0);
    const byte1 = decoded.charCodeAt(1);
    const isPK = byte0 === 0x50 && byte1 === 0x4B;
    
    console.log('Base64 archive check result:', {
      contentStart: content.substring(0, 20),
      firstBytes: [byte0, byte1],
      firstBytesHex: ['0x' + byte0.toString(16), '0x' + byte1.toString(16)],
      isPK: isPK,
      expectedPK: [0x50, 0x4B]
    });
    
    return isPK;
  } catch (error) {
      console.error('Base64 decode error in isBase64Archive:', error);
      console.log('Error details:', {
        message: (error as Error).message,
        contentLength: content.length,
        contentStart: content.substring(0, 50)
      });
      return false;
    }
};

const extractTextFromArchive = async (base64Content: string): Promise<string> => {
  try {
    console.log('Starting archive extraction, content length:', base64Content.length);
    
    // Декодируем base64 в бинарные данные
    const binaryString = atob(base64Content);
    console.log('Base64 decoded, binary length:', binaryString.length);
    
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    console.log('Converted to bytes array, first 10 bytes:', Array.from(bytes.slice(0, 10)).map(b => '0x' + b.toString(16)));
    
    // Загружаем ZIP-архив
    const zip = new JSZip();
    console.log('Loading ZIP archive...');
    const zipContent = await zip.loadAsync(bytes);
    console.log('ZIP loaded successfully');
    
    // Ищем файлы с текстовым содержимым
    const allFiles = Object.keys(zipContent.files);
    console.log('Files in archive:', allFiles);
    
    const textFiles = allFiles.filter(filename => {
      return filename.endsWith('.fb2') || 
             filename.endsWith('.epub');
    });
    console.log('Text files found:', textFiles);
    
    if (textFiles.length === 0) {
      console.log('No text files found in archive');
      return 'В архиве не найдено текстовых файлов';
    }
    
    // Извлекаем содержимое первого найденного файла
    const file = zipContent.files[textFiles[0]];
    console.log('Extracting content from file:', textFiles[0]);
    const content = await file.async('text');
    console.log('Content extracted, length:', content.length, 'first 100 chars:', content.substring(0, 100));
    
    return content;
  } catch (err) {
    console.error('Ошибка при извлечении текста из архива:', err);
    return 'Ошибка при обработке архива: ' + (err as Error).message;
  }
};

const isFB2Content = (content: string): boolean => {
  return content.includes('<FictionBook') || content.includes('<?xml');
};

const extractTextFromFB2 = (content: string): string => {
  const parser = new DOMParser();
  try {
    const doc = parser.parseFromString(content, 'text/xml');
    
    // Извлекаем заголовок книги
    const titleInfo = doc.querySelector('title-info');
    let result = '';
    
    if (titleInfo) {
      const bookTitle = titleInfo.querySelector('book-title')?.textContent;
      const authors = Array.from(titleInfo.querySelectorAll('author')).map(author => {
        const firstName = author.querySelector('first-name')?.textContent || '';
        const lastName = author.querySelector('last-name')?.textContent || '';
        return `${firstName} ${lastName}`.trim();
      }).filter(name => name);
      
      if (bookTitle) result += `# ${bookTitle}\n\n`;
      if (authors.length > 0) result += `**Автор:** ${authors.join(', ')}\n\n`;
    }
    
    // Извлекаем основной текст - пробуем разные варианты структуры FB2
    let textExtracted = false;
    
    // Вариант 1: стандартная структура с body > section
    const body = doc.querySelector('body');
    if (body) {
      const sections = body.querySelectorAll('section');
      if (sections.length > 0) {
        sections.forEach(section => {
          // Заголовки секций
          const titles = section.querySelectorAll('title');
          titles.forEach(title => {
            const titleText = title.textContent?.trim();
            if (titleText) result += `## ${titleText}\n\n`;
          });
          
          // Параграфы в секции
          const paragraphs = section.querySelectorAll('p');
          paragraphs.forEach(p => {
            const text = p.textContent?.trim();
            if (text) {
              result += `${text}\n\n`;
              textExtracted = true;
            }
          });
          
          // Также ищем текст в других элементах
          const textElements = section.querySelectorAll('subtitle, epigraph, poem, stanza, v');
          textElements.forEach(el => {
            const text = el.textContent?.trim();
            if (text) {
              result += `${text}\n\n`;
              textExtracted = true;
            }
          });
        });
      }
    }
    
    // Вариант 2: если не нашли текст в секциях, ищем напрямую все параграфы
    if (!textExtracted) {
      const allParagraphs = doc.querySelectorAll('p');
      allParagraphs.forEach(p => {
        const text = p.textContent?.trim();
        if (text) {
          result += `${text}\n\n`;
          textExtracted = true;
        }
      });
    }
    
    // Вариант 3: если всё ещё нет текста, извлекаем из любых текстовых элементов
    if (!textExtracted) {
      const textElements = doc.querySelectorAll('title, subtitle, p, v, text-author');
      textElements.forEach(el => {
        const text = el.textContent?.trim();
        if (text && text.length > 10) { // игнорируем очень короткие строки
          result += `${text}\n\n`;
          textExtracted = true;
        }
      });
    }
    
    // Если ничего не извлекли, возвращаем очищенный от тегов текст
    if (!textExtracted) {
      const cleanText = content.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
      if (cleanText.length > 100) {
        result += cleanText;
      }
    }
    
    return result || 'Не удалось извлечь текст из FB2 файла';
   } catch (err) {
     console.error('Ошибка при парсинге FB2:', err);
     return content.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
   }
 };

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

const fetchBookContent = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    const data = await getBookContent(Number(props.bookId));
    
    console.log('Fetched book data:', {
      title: data.title,
      author: data.author,
      contentLength: data.content.length,
      contentStart: data.content.substring(0, 50)
    });
    
    // Проверяем, является ли контент base64-закодированным архивом
    let processedContent = data.content;
    contentInfo.value = '';
    
    const isArchive = isBase64Archive(data.content);
    console.log('Is archive check result:', isArchive);
    
    if (isArchive) {
      console.log('Processing as ZIP archive...');
      contentInfo.value = 'Обработка ZIP-архива...';
      processedContent = await extractTextFromArchive(data.content);
      contentInfo.value = 'Архив успешно обработан';
      console.log('Archive processed, content length:', processedContent.length);
    }
    
    // Проверяем, является ли контент FB2 или XML
    const isFB2 = isFB2Content(processedContent);
    console.log('Is FB2 check result:', isFB2);
    
    if (isFB2) {
      console.log('Processing as FB2/XML...');
      contentInfo.value += (contentInfo.value ? ' • ' : '') + 'Обработка FB2/XML формата';
      processedContent = extractTextFromFB2(processedContent);
      console.log('FB2 processed, content length:', processedContent.length);
    }
    
    // Если контент выглядит как Markdown, обрабатываем его
    const isMarkdown = isMarkdownContent(processedContent);
    console.log('Is Markdown check result:', isMarkdown);
    
    if (isMarkdown) {
      console.log('Processing as Markdown...');
      renderedContent.value = await marked(processedContent);
    } else {
      console.log('Processing as plain text...');
      // Иначе отображаем как обычный текст с базовым форматированием
      renderedContent.value = formatPlainText(processedContent);
    }
    
    console.log('Final rendered content length:', renderedContent.value.length);
    
    bookTitle.value = data.title;
    bookAuthor.value = data.author;
  } catch (err: any) {
    console.error('Ошибка при загрузке книги:', err);
    error.value = 'Не удалось загрузить содержимое книги';
  } finally {
    isLoading.value = false;
  }
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

onMounted(async () => {
  loadFromStorage();
  await findUserBookId();
  await fetchBookContent();
  // Обновляем время каждую секунду для корректного отображения таймера
  timeInterval = setInterval(updateCurrentTime, 1000);
});

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval);
  }
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

.book-content {
  background: inherit;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  line-height: 1.8;
  font-size: 1.1rem;
  color: inherit;
}

.content-info {
  background: #e8f4fd;
  border: 1px solid #3498db;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 20px;
  color: #2980b9;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.content-info i {
  color: #3498db;
}

.book-content :deep(h1) {
  font-size: 2rem;
  margin-bottom: 20px;
  color: #2c3e50;
  text-align: center;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

.book-content :deep(h2) {
  font-size: 1.5rem;
  margin: 30px 0 15px 0;
  color: #34495e;
  border-left: 4px solid #3498db;
  padding-left: 15px;
}

.book-content :deep(h3) {
  font-size: 1.3rem;
  margin: 25px 0 10px 0;
  color: #34495e;
  font-style: italic;
}

.book-content :deep(p) {
  margin-bottom: 20px;
  text-align: justify;
}

.book-content :deep(strong) {
  color: #2c3e50;
}

.book-content :deep(em) {
  color: #6c757d;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

/* Стили для загрузки и ошибок */
.text-center {
  text-align: center;
}

.py-5 {
  padding-top: 3rem;
  padding-bottom: 3rem;
}

.mt-3 {
  margin-top: 1rem;
  color: inherit;
}

.alert {
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid transparent;
  border-radius: 0.375rem;
}

.alert-danger {
  color: #721c24;
  background-color: #f8d7da;
  border-color: #f5c6cb;
}

/* Стили для элементов загрузки и ошибок в темных темах */
.theme-dark .alert-danger,
.theme-night .alert-danger,
.theme-night-sepia .alert-danger {
  background-color: rgba(220, 53, 69, 0.2) !important;
  border-color: rgba(220, 53, 69, 0.3) !important;
  color: #f8d7da !important;
}

.theme-sepia .alert-danger {
  background-color: rgba(139, 69, 19, 0.1) !important;
  border-color: rgba(139, 69, 19, 0.2) !important;
  color: #8b4513 !important;
}

.theme-blue .alert-danger {
  background-color: rgba(220, 53, 69, 0.1) !important;
  border-color: rgba(220, 53, 69, 0.2) !important;
  color: #721c24 !important;
}

.theme-dark .spinner-border,
.theme-night .spinner-border,
.theme-night-sepia .spinner-border {
  color: #ecf0f1 !important;
}

.theme-sepia .spinner-border {
  color: #5d4e37 !important;
}

.theme-blue .spinner-border {
  color: #1e3a5f !important;
}



.me-2 {
  margin-right: 0.5rem;
}

.text-primary {
  color: #0d6efd;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.spinner-border {
  display: inline-block;
  width: 2rem;
  height: 2rem;
  vertical-align: -0.125em;
  border: 0.25em solid currentColor;
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
  font-size: 0.9rem !important;
}

.font-small :deep(h1) {
  font-size: 1.6rem !important;
}

.font-small :deep(h2) {
  font-size: 1.3rem !important;
}

.font-small :deep(h3) {
  font-size: 1.1rem !important;
}

.font-medium {
  font-size: 1.1rem !important;
}

.font-medium :deep(h1) {
  font-size: 2rem !important;
}

.font-medium :deep(h2) {
  font-size: 1.5rem !important;
}

.font-medium :deep(h3) {
  font-size: 1.3rem !important;
}

.font-large {
  font-size: 1.3rem !important;
}

.font-large :deep(h1) {
  font-size: 2.4rem !important;
}

.font-large :deep(h2) {
  font-size: 1.8rem !important;
}

.font-large :deep(h3) {
  font-size: 1.6rem !important;
}

/* Светлая тема */
.theme-light {
  color: #2c3e50 !important;
}

.theme-light .book-content {
  background: #fff !important;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
}

/* Темная тема */
.theme-dark {
  color: #ecf0f1 !important;
}

.theme-dark .book-content {
  background: #2c3e50 !important;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
}

.theme-dark :deep(h1),
.theme-dark :deep(h2),
.theme-dark :deep(h3) {
  color: #ecf0f1 !important;
}

.theme-dark :deep(strong) {
  color: #ecf0f1 !important;
}

.theme-dark :deep(em) {
  color: #bdc3c7 !important;
}

/* Сепия тема */
.theme-sepia {
  color: #5d4e37 !important;
}

.theme-sepia .book-content {
  background: #f4f1e8 !important;
  box-shadow: 0 4px 6px rgba(93, 78, 55, 0.1) !important;
}

.theme-sepia :deep(h1),
.theme-sepia :deep(h2),
.theme-sepia :deep(h3) {
  color: #5d4e37 !important;
}

.theme-sepia :deep(strong) {
  color: #4a3728 !important;
}

.theme-sepia :deep(em) {
  color: #8b7355 !important;
}

/* Ночная тема */
.theme-night {
  color: #b8c5d6 !important;
}

.theme-night .book-content {
  background: #0f0f23 !important;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5) !important;
}

.theme-night :deep(h1),
.theme-night :deep(h2),
.theme-night :deep(h3) {
  color: #b8c5d6 !important;
}

.theme-night :deep(strong) {
  color: #d4e2f0 !important;
}

.theme-night :deep(em) {
  color: #9aa8b5 !important;
}

/* Ночная сепия тема */
.theme-night-sepia {
  color: #d4a574 !important;
}

.theme-night-sepia .book-content {
  background: #1a1612 !important;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4) !important;
}

.theme-night-sepia :deep(h1),
.theme-night-sepia :deep(h2),
.theme-night-sepia :deep(h3) {
  color: #d4a574 !important;
}

.theme-night-sepia :deep(strong) {
  color: #e6b885 !important;
}

.theme-night-sepia :deep(em) {
  color: #c19a6b !important;
}

/* Синяя тема */
.theme-blue {
  color: #2c3e50 !important;
}

.theme-blue .book-content {
  background: #e8f4fd !important;
  box-shadow: 0 4px 6px rgba(30, 58, 95, 0.1) !important;
}

.theme-blue :deep(h1),
.theme-blue :deep(h2),
.theme-blue :deep(h3) {
  color: #1e3a5f !important;
}

.theme-blue :deep(strong) {
  color: #1e3a5f !important;
}

.theme-blue :deep(em) {
  color: #4a90e2 !important;
}

/* Кнопка отметки о чтении */
.reading-activity-button {
  position: fixed;
  bottom: 30px;
  left: 30px;
  z-index: 1000;
}

.reading-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #ffffff;
  padding: 12px 20px;
  border-radius: 50px;
  font-weight: 600;
  font-size: 0.9rem;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  display: flex;
  align-items: center;
  white-space: nowrap;
}

.reading-btn:hover:not(.disabled) {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.reading-btn.disabled {
  background: linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%);
  color: #7f8c8d;
  cursor: not-allowed;
  box-shadow: 0 4px 12px rgba(189, 195, 199, 0.3);
}

.reading-btn i {
  font-size: 1.1rem;
}

/* Стили для темных тем */
.theme-dark .reading-btn,
.theme-night .reading-btn,
.theme-night-sepia .reading-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: #ffffff;
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.theme-dark .reading-btn:hover:not(.disabled),
.theme-night .reading-btn:hover:not(.disabled),
.theme-night-sepia .reading-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #ee5a24 0%, #ff6b6b 100%);
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.5);
}

.theme-sepia .reading-btn {
  background: linear-gradient(135deg, #d4a574 0%, #c19653 100%);
  color: #5d4e37;
  box-shadow: 0 6px 20px rgba(212, 165, 116, 0.4);
}

.theme-sepia .reading-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #c19653 0%, #d4a574 100%);
  box-shadow: 0 8px 25px rgba(212, 165, 116, 0.5);
}

.theme-blue .reading-btn {
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  color: #ffffff;
  box-shadow: 0 6px 20px rgba(116, 185, 255, 0.4);
}

.theme-blue .reading-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #0984e3 0%, #74b9ff 100%);
  box-shadow: 0 8px 25px rgba(116, 185, 255, 0.5);
}

/* Стили для disabled состояния в темных темах */
.theme-dark .reading-btn.disabled,
.theme-night .reading-btn.disabled,
.theme-night-sepia .reading-btn.disabled,
.theme-blue .reading-btn.disabled {
  background: linear-gradient(135deg, #4a4a4a 0%, #2c2c2c 100%);
  color: #888888;
  box-shadow: 0 4px 12px rgba(74, 74, 74, 0.3);
}

.theme-sepia .reading-btn.disabled {
  background: linear-gradient(135deg, #a0906b 0%, #8b7d5a 100%);
  color: #6b5d42;
  box-shadow: 0 4px 12px rgba(160, 144, 107, 0.3);
}

@media (max-width: 768px) {
  .book-reader {
    padding: 15px;
  }
  
  .book-content {
    padding: 20px;
  }
  
  .book-title {
    font-size: 2rem;
  }
  
  .reading-activity-button {
    bottom: 20px;
    left: 20px;
  }
  
  .reading-btn {
    padding: 10px 16px;
    font-size: 0.8rem;
  }
}
</style>