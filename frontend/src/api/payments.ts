import axiosInstance from '@/plugins/axios';

export interface PremiumPlan {
  id: number;
  name: string;
  description: string;
  price: number;
  duration_days: number;
  features: string[];
}

export interface Payment {
  id: string;
  user: any;
  plan: PremiumPlan;
  amount: number;
  currency: string;
  status: string;
  payment_url?: string;
  created_at: string;
  paid_at?: string;
}

export interface CreatePaymentResponse {
  payment_id: string;
  payment_url: string;
  amount: number;
  status: string;
}

// Получить список тарифных планов
export const getPremiumPlans = async (): Promise<PremiumPlan[]> => {
  const response = await axiosInstance.get('payments/plans/');
  return response.data;
};

// Создать платеж
export const createPayment = async (planId: number): Promise<CreatePaymentResponse> => {
  const response = await axiosInstance.post('payments/create/', {
    plan_id: planId
  });
  return response.data;
};

// Получить список платежей пользователя
export const getUserPayments = async (): Promise<Payment[]> => {
  const response = await axiosInstance.get('payments/list/');
  return response.data;
};

// Проверить статус платежа
export const getPaymentStatus = async (paymentId: string): Promise<Payment> => {
  const response = await axiosInstance.get(`payments/status/${paymentId}/`);
  return response.data;
};
