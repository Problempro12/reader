import axios from 'axios';
import type { Book, BookFilters, BookResponse, BookCreate, BookUpdate } from '@/types/book';

const API_URL = 'http://localhost:8000/api';

export interface BooksResponse {
  books: Book[];
  total: number;
  page: number;
  perPage: number;
}

// Получение списка книг с фильтрацией и пагинацией
export const getBooks = async (filters: BookFilters): Promise<BooksResponse> => {
  const { data } = await axios.get(`${API_URL}/books`, { params: filters });
  return data;
};

// Получение топ книг
export const getTopBooks = async (limit: number = 5): Promise<Book[]> => {
  const { data } = await axios.get(`${API_URL}/books/top`);
  return data;
};

// Получение рекомендуемых книг
export const getRecommendedBooks = async (limit: number = 5): Promise<Book[]> => {
  const { data } = await axios.get(`${API_URL}/books/recommended`);
  return data;
};

// Получение книги по ID
export const getBook = async (id: number): Promise<Book> => {
  const { data } = await axios.get(`${API_URL}/books/${id}`);
  return data;
};

// Создание новой книги
export const createBook = async (book: BookCreate): Promise<Book> => {
  const response = await axios.post(`${API_URL}/books/`, book);
  return response.data;
};

// Обновление книги
export const updateBook = async (book: BookUpdate): Promise<Book> => {
  const response = await axios.put(`${API_URL}/books/${book.id}/`, book);
  return response.data;
};

// Удаление книги
export const deleteBook = async (id: number): Promise<void> => {
  const response = await axios.delete(`${API_URL}/books/${id}/`);
  return response.data;
};

// Оценка книги
export const rateBook = async (bookId: number, rating: number): Promise<void> => {
  await axios.post(`${API_URL}/books/${bookId}/rate`, { rating });
};

export const booksApi = {
  async getBooks(params: {
    page?: number;
    perPage?: number;
    search?: string;
    genre?: string;
    ageCategory?: string;
    rating?: number;
    sortBy?: string;
  }): Promise<BooksResponse> {
    const { data } = await axios.get(`${API_URL}/books`, { params });
    return data;
  },

  async getTopBooks(): Promise<Book[]> {
    const { data } = await axios.get(`${API_URL}/books/top`);
    return data;
  },

  async getRecommendedBooks(): Promise<Book[]> {
    const { data } = await axios.get(`${API_URL}/books/recommended`);
    return data;
  },

  async rateBook(bookId: number, rating: number): Promise<void> {
    await axios.post(`${API_URL}/books/${bookId}/rate`, { rating });
  }
}; 