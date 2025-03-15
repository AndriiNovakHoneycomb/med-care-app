import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (email: string, password: string, name: string) =>
    api.post('/auth/register', { email, password, name }),
  getProfile: () => api.get('/auth/me'),
};

// Patients API
export const patientsApi = {
  getPatients: (params?: any) => api.get('/patients', { params }),
  approvePatient: (id: string) => api.patch(`/patients/${id}/approve`),
  updatePatient: (id: string, data: any) => api.put(`/patients/${id}`, data),
  deletePatient: (id: string) => api.delete(`/patients/${id}`),
  createPatient: (data: any) => api.post('/patients', data),
}; 