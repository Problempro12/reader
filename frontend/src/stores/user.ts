import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@/types';
import axios from 'axios';

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
    authToken.value = token;
    userData.value = user;
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(user));
  };

  const clearAuthData = () => {
    authToken.value = null;
    userData.value = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  };

  // Функция для загрузки данных пользователя с бэкенда
  const fetchUserData = async () => {
    if (authToken.value) {
      try {
        const response = await axios.get('http://localhost:8000/api/users/me/', {
          headers: {
            'Authorization': `Token ${authToken.value}`
          }
        });
        userData.value = response.data;
        localStorage.setItem('user', JSON.stringify(response.data));
      } catch (error) {
        console.error('Ошибка при загрузке данных пользователя:', error);
        clearAuthData(); // Очистить данные, если загрузка не удалась (например, токен недействителен)
        // Здесь можно добавить перенаправление на страницу входа, если нужно
      }
    }
  };

  // При инициализации стора или обновлении страницы, пытаемся загрузить данные
  // Если токен есть, но данных пользователя нет (например, после перезагрузки)
   if (authToken.value && !userData.value) {
     fetchUserData();
   }

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