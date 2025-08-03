import axiosInstance from '@/plugins/axios';
import type { Book, BookFilters, BookResponse, BookCreate, BookUpdate } from '@/types/book';

// Получение списка книг с фильтрацией и пагинацией
export const getBooks = async (filters: BookFilters): Promise<BookResponse> => {
  const response = await axiosInstance.get('books/', { params: filters });
  return response.data;
};

// Получение топ книг
export const getTopBooks = async (limit: number = 5): Promise<Book[]> => {
  const { data } = await axiosInstance.get('books/top', { params: { limit } });
  return data;
};

// Получение рекомендуемых книг
export const getRecommendedBooks = async (limit: number = 5): Promise<Book[]> => {
  const { data } = await axiosInstance.get('books/recommended', { params: { limit } });
  return data;
};

// Получение книги по ID
export const getBook = async (id: number): Promise<Book> => {
  const { data } = await axiosInstance.get(`books/${id}`);
  return data;
};

// Создание новой книги
export const createBook = async (book: BookCreate): Promise<Book> => {
  const response = await axiosInstance.post('books/', book);
  return response.data;
};

// Обновление книги
export const updateBook = async (book: BookUpdate): Promise<Book> => {
  const response = await axiosInstance.put(`books/${book.id}/`, book);
  return response.data;
};

// Удаление книги
export const deleteBook = async (id: number): Promise<void> => {
  const response = await axiosInstance.delete(`books/${id}/`);
  return response.data;
};

// Получение рейтинга книги
export const getBookRating = async (bookId: number): Promise<{user_rating: number | null, average_rating: number, rating_count: number}> => {
  const { data } = await axiosInstance.get(`books/${bookId}/rating/`);
  return data;
};

// Оценка книги
export const rateBook = async (bookId: number, rating: number): Promise<Book> => {
  const { data } = await axiosInstance.post(`books/${bookId}/rate/`, { rating });
  return data;
};

// Запуск скрипта импорта книг
export const runImportScript = async (query: string = 'популярные книги'): Promise<any> => {
  const response = await axiosInstance.post('books/run-import-script/', { query });
  return response.data;
};

// Получение списка жанров
export const getGenres = async (): Promise<string[]> => {
  const { data } = await axiosInstance.get('books/genres/');
  return data;
};

// Получение списка возрастных категорий
export const getAgeCategories = async (): Promise<string[]> => {
  const { data } = await axiosInstance.get('books/age_categories/');
  return data;
};

// Голосование за книгу
export const voteForBook = async (bookId: number): Promise<{message: string, vote_count: number}> => {
  const { data } = await axiosInstance.post(`books/${bookId}/vote/`);
  return data;
};

// Отмена голоса за книгу
export const removeVoteForBook = async (bookId: number): Promise<{message: string, vote_count: number}> => {
  const { data } = await axiosInstance.post(`books/${bookId}/remove_vote/`);
  return data;
};

// Получение информации о голосах за книгу
export const getBookVoteInfo = async (bookId: number): Promise<{vote_count: number, user_voted: boolean}> => {
  const { data } = await axiosInstance.get(`books/${bookId}/vote_info/`);
  return data;
};

// Получение топ книг по голосам
export const getTopVotedBooks = async (limit: number = 5): Promise<Book[]> => {
  const { data } = await axiosInstance.get('books/top_voted/', { params: { limit } });
  return data;
};

// Получение книги недели
export const getBookOfWeek = async (): Promise<Book> => {
  const { data } = await axiosInstance.get('books/current_week/');
  return data;
};