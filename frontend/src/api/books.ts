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

// Оценка книги
export const rateBook = async (bookId: number, rating: number): Promise<Book> => {
  const { data } = await axiosInstance.post(`books/${bookId}/rate`, { rating });
  return data;
}; 

// Запуск скрипта импорта книг
export const runImportScript = async (): Promise<any> => {
  const response = await axiosInstance.post('books/run-import-script/');
  return response.data;
}; 