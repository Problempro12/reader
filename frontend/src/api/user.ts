import axiosInstance from '@/plugins/axios';

export const fetchUserData = async () => {
    try {
        const response = await axiosInstance.get('/users/me/');
        return response.data;
    } catch (error) {
        console.error('Ошибка при получении данных пользователя:', error);
        throw error;
    }
};

export const updateUserProfile = async (data: any) => {
    try {
        const response = await axiosInstance.patch('/users/me/', data);
        return response.data;
    } catch (error) {
        console.error('Store: Ошибка при обновлении профиля:', error);
        throw error;
    }
};

export const login = async (credentials: { email: string; password: string }) => {
    try {
        const response = await axiosInstance.post('/users/login/', credentials);
        return response.data;
    } catch (error) {
        console.error('Store: Ошибка при входе:', error);
        throw error;
    }
};

export const register = async (userData: { email: string; password: string; username: string }) => {
    try {
        const response = await axiosInstance.post('/users/register/', userData);
        return response.data;
    } catch (error) {
        console.error('Store: Ошибка при регистрации:', error);
        throw error;
    }
}; 