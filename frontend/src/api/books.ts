import axiosInstance from '@/plugins/axios';
import type { Book, BookFilters, BookResponse, BookCreate, BookUpdate } from '@/types/book';

// Получение списка книг с фильтрацией и пагинацией
export const getBooks = async (filters: BookFilters): Promise<BookResponse> => {
  const response = await axiosInstance.get('books/books/', { params: filters });
  return response.data;
};

// Получение топ книг
export const getTopBooks = async (limit: number = 5): Promise<Book[]> => {
  const { data } = await axiosInstance.get('books/books/top', { params: { limit } });
  return data;
};

// Получение рекомендуемых книг
export const getRecommendedBooks = async (limit: number = 5): Promise<Book[]> => {
  const { data } = await axiosInstance.get('books/books/recommended', { params: { limit } });
  return data;
};

// Получение книги по ID
export const getBook = async (id: number): Promise<Book> => {
  const { data } = await axiosInstance.get(`books/books/${id}`);
  return data;
};

// Создание новой книги
export const createBook = async (book: BookCreate): Promise<Book> => {
  const response = await axiosInstance.post('books/books/', book);
  return response.data;
};

// Обновление книги
export const updateBook = async (book: BookUpdate): Promise<Book> => {
  const response = await axiosInstance.put(`books/books/${book.id}/`, book);
  return response.data;
};

// Удаление книги
export const deleteBook = async (id: number): Promise<void> => {
  const response = await axiosInstance.delete(`books/books/${id}/`);
  return response.data;
};

// Получение рейтинга книги
export const getBookRating = async (bookId: number): Promise<{user_rating: number | null, average_rating: number, rating_count: number}> => {
  const { data } = await axiosInstance.get(`books/books/${bookId}/rating/`);
  return data;
};

// Оценка книги
export const rateBook = async (bookId: number, rating: number): Promise<Book> => {
  const { data } = await axiosInstance.post(`books/books/${bookId}/rate/`, { rating });
  return data;
};

// Запуск скрипта импорта книг
export const runImportScript = async (query: string = 'популярные книги'): Promise<any> => {
  const response = await axiosInstance.post('books/books/run-import-script/', { query });
  return response.data;
};

// Получение списка жанров
export const getGenres = async (): Promise<string[]> => {
  const { data } = await axiosInstance.get('books/books/genres/');
  return data;
};

// Получение списка возрастных категорий
export const getAgeCategories = async (): Promise<string[]> => {
  const { data } = await axiosInstance.get('books/books/age_categories/');
  return data;
};

// Голосование за книгу
export const voteForBook = async (bookId: number): Promise<{message: string, vote_count: number}> => {
  const { data } = await axiosInstance.post(`books/books/${bookId}/vote/`);
  return data;
};

// Отмена голоса за книгу
export const removeVoteForBook = async (bookId: number): Promise<{message: string, vote_count: number}> => {
  const { data } = await axiosInstance.delete(`books/books/${bookId}/remove_vote/`);
  return data;
};

// Получение информации о голосах за книгу
export const getBookVoteInfo = async (bookId: number): Promise<{vote_count: number, user_voted: boolean}> => {
  const { data } = await axiosInstance.get(`books/books/${bookId}/vote_info/`);
  return data;
};

// Получение топ книг по голосам
export const getTopVotedBooks = async (limit: number = 5): Promise<Book[]> => {
  const { data } = await axiosInstance.get('books/books/top_voted/', { params: { limit } });
  return data;
};

// Получение книги недели
export const getBookOfWeek = async (): Promise<Book> => {
  const { data } = await axiosInstance.get('books/books/current_week/');
  return data;
};

// Получение содержимого книги для чтения
export const getBookContent = async (id: number): Promise<{id: number, title: string, author: string, content: string}> => {
  const { data } = await axiosInstance.get(`books/books/${id}/content/`);
  return data;
};

// === USER BOOKS API ===

// Получение книг пользователя
export const getUserBooks = async (status?: string): Promise<any[]> => {
  const params = status ? { status } : {};
  const { data } = await axiosInstance.get('books/user-books/', { params });
  return data;
};

// Добавление книги в библиотеку пользователя
export const addUserBook = async (bookId: number, status: string = 'planned'): Promise<any> => {
  const { data } = await axiosInstance.post('books/user-books/', {
    book: bookId,
    status
  });
  return data;
};

// Обновление статуса книги пользователя
export const updateUserBookStatus = async (userBookId: number, status: string): Promise<any> => {
  const { data } = await axiosInstance.patch(`books/user-books/${userBookId}/`, { status });
  return data;
};

// === READING PROGRESS API ===

// Получение прогресса чтения
export const getReadingProgress = async (): Promise<any[]> => {
  const { data } = await axiosInstance.get('books/reading-progress/');
  return data;
};

// Добавление отметки о прогрессе чтения
export const addReadingProgress = async (userBookId: number, position: number): Promise<any> => {
  const { data } = await axiosInstance.post('books/reading-progress/', {
    user_book: userBookId,
    position
  });
  return data;
};

// Получение статистики чтения
export const getReadingStats = async (): Promise<{total_marks: number, total_hours: number}> => {
  const { data } = await axiosInstance.get('books/reading-progress/');
  const totalMarks = data.length;
  const totalHours = Math.floor(totalMarks / 4); // 4 отметки = 1 час
  return {
    total_marks: totalMarks,
    total_hours: totalHours
  };
};

// Получение всех категорий Flibusta
export const getFlibustCategories = async (): Promise<{success: boolean, categories: any[], count: number, error?: string}> => {
  const { data } = await axiosInstance.get('books/books/flibusta_categories/');
  return data;
};

// Массовый импорт книг из категории
export const importCategoryBooks = async (categoryUrl: string, count: number): Promise<any> => {
  const response = await axiosInstance.post('books/books/import_category_books/', {
    category_url: categoryUrl,
    count: count
  });
  return response.data;
};