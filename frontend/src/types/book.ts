export interface Book {
  id: number;
  title: string;
  author: string;
  cover: string;
  genre: string;
  ageCategory: string;
  description: string;
  isPremium: boolean;
  rating: number;
  litresRating?: {
    value: number;
    count: number;
  };
  series?: string;
  translator?: string;
  ratingCount?: number;
  reviewsCount?: number;
  price?: {
    current: string;
    discount: string;
    subscriber: string;
  };
  technical?: {
    volume: string;
    year: string;
    isbn: string;
    copyrightHolder: string;
  };
}

export interface BookFilters {
  search?: string;
  genre?: string;
  ageCategory?: string;
  page?: number;
  limit?: number;
}

export interface BookResponse {
  books: Book[];
  total: number;
  page: number;
  limit: number;
}

export interface BookCreate {
  title: string;
  author: string;
  cover: string;
  genre: string;
  ageCategory: string;
  description: string;
  isPremium: boolean;
  litresRating?: {
    value: number;
    count: number;
  };
  series?: string;
  translator?: string;
  rating?: number;
  ratingCount?: number;
  reviewsCount?: number;
  price?: {
    current: string;
    discount: string;
    subscriber: string;
  };
  technical?: {
    volume: string;
    year: string;
    isbn: string;
    copyrightHolder: string;
  };
}

export interface BookUpdate extends Partial<BookCreate> {
  id: number;
} 