// Определение базового типа пользователя
export interface User {
  id: number;
  email: string;
  username: string;
  is_premium: boolean;
  premium_expiration_date: string | null;
  hide_ads: boolean;
  avatar_url: string | null;
  about: string | null;
  stats?: BookStats; // stats is optional and should match BookStats interface
  is_staff: boolean;
  is_superuser: boolean;
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