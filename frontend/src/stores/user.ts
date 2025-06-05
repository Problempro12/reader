import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import type { User } from '@/types';
import axiosInstance from '@/plugins/axios';

interface User {
  id: number
  username: string
  email: string
  stats: {
    reading: number
    completed: number
    planned: number
  }
}

export const useUserStore = defineStore('user', () => {
  const authToken = ref<string | null>(localStorage.getItem('authToken'));
  const userData = ref<User | null>(localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user') as string) : null);

  const isLoggedIn = computed(() => authToken.value !== null);
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
    if (!authToken.value) return;
    
    try {
      console.log('Store: запрос данных пользователя...')
      const response = await axiosInstance.get('users/me/');
      console.log('Store: получены данные пользователя:', response.data)
      console.log('Store: проверка прав администратора:', {
        is_staff: response.data.is_staff,
        is_superuser: response.data.is_superuser
      })
      
      userData.value = response.data;
      localStorage.setItem('user', JSON.stringify(response.data));
      
      // Проверяем данные после сохранения
      console.log('Store: данные после обновления:', {
        userData: userData.value,
        isAdmin: userData.value?.is_staff || userData.value?.is_superuser
      })
    } catch (error) {
      console.error('Ошибка при загрузке данных пользователя:', error);
      clearAuthData();
    }
  };

  // Следим за изменением токена и загружаем данные пользователя при необходимости
  watch(authToken, (newToken) => {
    if (newToken && !userData.value) {
      fetchUserData();
    }
  }, { immediate: true });

  return {
    authToken,
    userData,
    isLoggedIn,
    userInitials,
    setAuthData,
    clearAuthData,
    fetchUserData,
  };
}); 