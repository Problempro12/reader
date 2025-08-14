import axiosInstance from '@/plugins/axios';

export interface Achievement {
  id: number;
  title: string;
  description: string;
  icon_url: string;
  category: 'READING' | 'BOOKS' | 'SOCIAL' | 'OTHER';
  requirement: any;
  created_at: string;
}

export interface UserAchievement {
  id: number;
  user: number;
  achievement: Achievement;
  earned_at: string;
}

export interface AchievementProgress {
  achievement_id: number;
  progress: number;
  max_progress: number;
  completed: boolean;
}

export const fetchUserAchievements = async (): Promise<UserAchievement[]> => {
  try {
    const response = await axiosInstance.get('/achievements/user-achievements/')
    return response.data
  } catch (error) {
    console.error('Ошибка при получении достижений пользователя:', error)
    throw error
  }
};

export const fetchAllAchievements = async (): Promise<Achievement[]> => {
  try {
    const response = await axiosInstance.get('/achievements/achievements/')
    return response.data
  } catch (error) {
    console.error('Ошибка при получении всех достижений:', error)
    throw error
  }
};

export const checkAchievements = async (): Promise<any> => {
  try {
    const response = await axiosInstance.post('/achievements/check/')
    return response.data
  } catch (error) {
    console.error('Ошибка при проверке достижений:', error)
    throw error
  }
};

export const fetchUserStats = async (): Promise<any> => {
  try {
    const response = await axiosInstance.get('/users/me/')
    const userData = response.data
    
    // Вычисляем статистику на основе данных пользователя
    const stats = {
      reading_hours: Math.floor((userData.stats?.progress_marks_count || 0) / 4), // 4 отметки = 1 час
      books_rated: userData.stats?.read_count || 0,
      votes_cast: 0 // Пока заглушка, можно добавить API для голосов
    }
    
    return stats
  } catch (error) {
    console.error('Ошибка при получении статистики пользователя:', error)
    throw error
  }
};