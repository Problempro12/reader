import axiosInstance from '@/plugins/axios';
import type { Book, BookFilters, BookResponse, BookCreate, BookUpdate } from '@/types/book';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

// Получение списка книг с фильтрацией и пагинацией
export const getBooks = async (filters: BookFilters): Promise<BookResponse> => {
  const response = await axiosInstance.get('books/', { params: filters });
  return response.data;
};

// Получение топ книг
export const getTopBooks = async (limit: number = 5): Promise<Book[]> => {
  const { data } = await axiosInstance.get(`${API_URL}/books/top`, { params: { limit } });
  return data;
};

// Получение рекомендуемых книг
export const getRecommendedBooks = async (limit: number = 5): Promise<Book[]> => {
  const { data } = await axiosInstance.get(`${API_URL}/books/recommended`, { params: { limit } });
  return data;
};

// Получение книги по ID
export const getBook = async (id: number): Promise<Book> => {
  const { data } = await axiosInstance.get(`${API_URL}/books/${id}`);
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

// Оценка книги
export const rateBook = async (bookId: number, rating: number): Promise<Book> => {
  const { data } = await axiosInstance.post(`${API_URL}/books/${bookId}/rate`, { rating });
  return data;
}; 