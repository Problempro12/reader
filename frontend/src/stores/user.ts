import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import type { User } from '@/types';
import axiosInstance from '@/plugins/axios';
import axios from 'axios';

// Обновляем тип данных пользователя, ожидаемых от бэкенда
interface UserData {
  id: number;
  email: string;
  username: string;
  is_premium: boolean;
  premium_expiration_date: string | null;
  hide_ads: boolean;
  // Заменяем 'avatar' на 'avatar_url'
  avatar_url: string | null;
  about: string | null;
  stats?: { // Предполагаем, что stats может быть необязательным
    read_count: number;
    planning_count: number;
    reading_count: number;
    dropped_count: number;
    total_count: number;
  } | null;
  is_staff: boolean;
  is_superuser: boolean;
}

export const useUserStore = defineStore('user', () => {
  // Инициализируем состояние из localStorage или дефолтными значениями
  const authToken = ref<string | null>(localStorage.getItem('authToken'));
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'));
  // Удаляем старые данные пользователя из localStorage, чтобы избежать проблем с устаревшим форматом
  localStorage.removeItem('user');
  // Используем новый тип UserData
  const userData = ref<UserData | null>(null);
  const isLoggedIn = computed(() => authToken.value !== null);
  const isAdmin = computed(() => userData.value?.is_staff === true || userData.value?.is_superuser === true);
  const userInitials = computed(() => {
    if (userData.value && userData.value.username) {
      const nameParts = userData.value.username.split(' ');
      if (nameParts.length > 1) {
        return (nameParts[0][0] + nameParts[1][0]).toUpperCase();
      } else if (nameParts[0]) {
        return nameParts[0].substring(0, 2).toUpperCase();
      }
    }
    return '';
  });

  const setAuthData = (token: string, user: User) => {
    console.log('Store: установка данных аутентификации:', { token: token ? 'Присутствует' : 'Отсутствует', user })
    authToken.value = token;
    userData.value = user;
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(user));
    
    // Обновляем токен в axios
    if (token) {
      axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axiosInstance.defaults.headers.common['Authorization'];
    }
    
    // Проверяем данные после сохранения
    console.log('Store: данные после сохранения:', {
      authToken: authToken.value ? 'Присутствует' : 'Отсутствует',
      userData: userData.value,
      isAdmin: userData.value?.is_staff || userData.value?.is_superuser
    })
  };

  const clearAuthData = () => {
    authToken.value = null;
    userData.value = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    localStorage.removeItem('refreshToken');
    delete axiosInstance.defaults.headers.common['Authorization'];
  };

  // Функция для загрузки данных пользователя с бэкенда
  const fetchUserData = async () => {
    console.log('Store: запрос данных пользователя...');
    if (!authToken.value) {
      console.log('Store: Нет токена авторизации, пропускаем фетч данных пользователя.');
      userData.value = null;
      return; // Не фетчим, если нет токена
    }
    try {
      const response = await axiosInstance.get('/users/me/', {
        headers: {
          'Authorization': `Bearer ${authToken.value}`
        }
      });
      console.log('Store: получены данные пользователя:', response.data);
      userData.value = response.data; // Обновляем данные пользователя в сторе

      console.log('Store: проверка прав администратора:', { is_staff: userData.value?.is_staff, is_superuser: userData.value?.is_superuser });
      // Здесь можно добавить дополнительную логику или проверку данных
      console.log('Store: данные пользователя обновлены. URL аватара:', userData.value?.avatar_url); // Актуальный лог
    } catch (error) {
      console.error('Store: Ошибка при получении данных пользователя:', error);
      // Если токен невалидный, возможно, стоит выйти из системы
      if (axios.isAxiosError(error) && error.response?.status === 401) {
         clearAuthData(); // Выход при невалидном токене - вызываем clearAuthData
      }
      userData.value = null;
    }
  };

  const updateAvatar = async (file: File): Promise<void> => {
    console.log('Store: Начало загрузки аватара');
    const formData = new FormData();
    formData.append('avatar', file);

    try {
      console.log('Store: Отправка PATCH запроса на users/me/ с файлом:', file);
      const response = await axiosInstance.patch('/users/me/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${authToken.value}`
        },
      });
      console.log('Store: PATCH запрос успешен, получен ответ:', response.data);
      
      // Обновляем данные пользователя в сторе из ответа
      userData.value = response.data;
      console.log('Store: userData в сторе обновлено:', userData.value);
      console.log('Store: Аватар успешно обновлен. URL аватара после обновления:', userData.value?.avatar_url); // Актуальный лог

      // После успешного обновления, возможно, стоит снова получить полные данные пользователя
      // для синхронизации всех полей, хотя PATCH должен вернуть актуальные данные.
      // fetchUserData(); // Этот вызов теперь избыточен, так как PATCH возвращает актуальные данные

    } catch (error) {
      console.error('Store: Ошибка при загрузке аватара:', error);
      throw error; // Перебрасываем ошибку для обработки в компоненте
    }
  };

  // Следим за изменением токена и загружаем данные пользователя при необходимости
  watch(authToken, (newToken) => {
    if (newToken && !userData.value) {
      fetchUserData();
    }
  }, { immediate: true });

  const logout = async () => {
    try {
      // Можно добавить запрос на бэкенд для инвалидации токена
      authToken.value = null;
      userData.value = null;
      refreshToken.value = null;
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      localStorage.removeItem('refreshToken');
    } catch (error) {
      console.error('Ошибка при выходе из аккаунта:', error);
      throw error;
    }
  };

  const deleteAccount = async () => {
    try {
      await axios.delete('/api/users/profile/');
      authToken.value = null;
      userData.value = null;
      refreshToken.value = null;
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      localStorage.removeItem('refreshToken');
    } catch (error) {
      console.error('Ошибка при удалении аккаунта:', error);
      throw error;
    }
  };

  return {
    authToken,
    userData,
    isLoggedIn,
    isAdmin,
    userInitials,
    setAuthData,
    clearAuthData,
    fetchUserData,
    updateAvatar,
    logout,
    deleteAccount,
  };
}); 