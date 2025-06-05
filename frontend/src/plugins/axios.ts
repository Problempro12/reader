import axios from 'axios';
import router from '@/router';

// Создаем экземпляр axios с базовым URL
const axiosInstance = axios.create({
  baseURL: '/api/',
});

// Добавляем интерсептор для автоматического добавления токена
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    console.error('Ошибка при выполнении запроса:', error);
    return Promise.reject(error);
  }
);

// Добавляем интерсептор для обработки ошибок авторизации
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    console.error('Ошибка ответа:', error);
    
    if (error.code === 'ERR_NETWORK') {
      console.error('Ошибка сети. Проверьте, запущен ли сервер.');
      return Promise.reject(new Error('Ошибка сети. Проверьте, запущен ли сервер.'));
    }
    
    const originalRequest = error.config;
    
    // Если ошибка 401 и это не повторный запрос
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Пробуем обновить токен
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post('/api/token/refresh/', {
            refresh: refreshToken
          });
          
          const { access } = response.data;
          localStorage.setItem('authToken', access);
          
          // Повторяем оригинальный запрос с новым токеном
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return axiosInstance(originalRequest);
        }
      } catch (refreshError) {
        console.error('Ошибка обновления токена:', refreshError);
        // Если не удалось обновить токен, очищаем данные и перенаправляем на вход
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        
        if (router.currentRoute.value.path !== '/auth/login') {
          router.push('/auth/login');
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export default axiosInstance; 