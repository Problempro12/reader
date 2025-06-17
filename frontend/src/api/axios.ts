import axios from 'axios';
import { useUserStore } from '@/stores/user';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',  // Базовый URL бэкенда
  headers: {
    'Content-Type': 'application/json',
  },
});

// Перехватчик запросов
api.interceptors.request.use(
  (config) => {
    const userStore = useUserStore();
    const token = userStore.token;
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Перехватчик ответов
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Ошибка ответа:', error.config.url, error.response?.status);
    
    if (error.response?.status === 401) {
      const userStore = useUserStore();
      userStore.logout();
    }
    
    return Promise.reject(error);
  }
);

export default api; 