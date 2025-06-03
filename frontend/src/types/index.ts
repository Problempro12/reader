// Определение базового типа пользователя
export interface User {
  id: number;
  email: string;
  username: string;
  is_premium: boolean;
  premium_expiration_date: string | null;
  hide_ads: boolean;
  avatar?: string; // Необязательное поле для URL аватарки
  stats?: BookStats; // Добавляем поле для статистики книг
}

// Определение типа для статистики книг
export interface BookStats {
  read_count: number;
  planning_count: number;
  reading_count: number;
  dropped_count: number;
  total_count: number;
}

// Можете добавить другие типы здесь по мере необходимости 