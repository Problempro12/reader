export interface Book {
  id: number;
  title: string;
  author: {
    id: number;
    name: string;
    bio?: string;
    photo_url?: string;
  };
  cover: string;
  genre: string;
  ageCategory: string;
  description: string;
  isPremium: boolean;
  rating: number;
  vote_count?: number;
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
  rating?: number;
  sortBy?: string;
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
  author: number;
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