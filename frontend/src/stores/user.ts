import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import type { User } from '@/types';
import api from '@/api/axios';

// Обновляем тип данных пользователя, ожидаемых от бэкенда
interface UserData {
  id: number;
  email: string;
  username: string;
  is_premium: boolean;
  premium_expiration_date: string | null;
  hide_ads: boolean;
  avatar_url: string | null;
  about: string | null;
  stats?: {
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
  const authToken = ref<string | null>(localStorage.getItem('authToken'));
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'));
  localStorage.removeItem('user');
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
    
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete api.defaults.headers.common['Authorization'];
    }
    
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
    delete api.defaults.headers.common['Authorization'];
  };

  const fetchUserData = async () => {
    console.log('Store: запрос данных пользователя...');
    if (!authToken.value) {
      console.log('Store: Нет токена авторизации, пропускаем фетч данных пользователя.');
      userData.value = null;
      return;
    }
    try {
      const response = await api.get('/users/me/');
      console.log('Store: получены данные пользователя:', response.data);
      userData.value = response.data;

      console.log('Store: проверка прав администратора:', { is_staff: userData.value?.is_staff, is_superuser: userData.value?.is_superuser });
      console.log('Store: данные пользователя обновлены. URL аватара:', userData.value?.avatar_url);
    } catch (error) {
      console.error('Store: Ошибка при получении данных пользователя:', error);
      if (error.response?.status === 401) {
        clearAuthData();
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
      const response = await api.patch('/users/me/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log('Store: PATCH запрос успешен, получен ответ:', response.data);
      
      userData.value = response.data;
      console.log('Store: userData в сторе обновлено:', userData.value);
      console.log('Store: Аватар успешно обновлен. URL аватара после обновления:', userData.value?.avatar_url);

    } catch (error) {
      console.error('Store: Ошибка при загрузке аватара:', error);
      throw error;
    }
  };

  watch(authToken, (newToken) => {
    if (newToken && !userData.value) {
      fetchUserData();
    }
  }, { immediate: true });

  const logout = async () => {
    try {
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
      await api.delete('/users/me/');
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