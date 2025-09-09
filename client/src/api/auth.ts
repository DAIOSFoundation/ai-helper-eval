import apiClient from './client';

export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  role?: string;
}

export interface AuthResponse {
  user: User;
  message: string;
}

export const authAPI = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },

  register: async (userData: RegisterRequest): Promise<{ user_id: string; message: string }> => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  },

  getCurrentUser: (): User | null => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  setAuthToken: (token: string) => {
    localStorage.setItem('auth_token', token);
  },

  setUser: (user: User) => {
    localStorage.setItem('user', JSON.stringify(user));
  }
};
