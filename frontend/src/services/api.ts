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

interface GetPatientsParams {
  status: 'Approved' | 'Unapproved';
  search?: string;
}

interface GetAdminsParams {
  search?: string;
}

export const patientsApi = {
  getPatients: async ({ status, search }: GetPatientsParams): Promise<any> => {
    const { data } = await api.get('/patients', {
      params: {
        status,
        search,
      },
    });
    return data;
  },

  approvePatient: async (id: string): Promise<void> => {
    await api.patch(`/patients/${id}/status`);
  },

  deletePatient: async (id: string): Promise<void> => {
    await api.delete(`/patients/${id}`);
  },
};

export const adminsApi = {
  getAdmins: async ({ search }: GetAdminsParams): Promise<any> => {
    const { data } = await api.get('/admins/all', {
      params: {
        search,
      },
    });
    return data;
  },

  deleteAdmin: async (id: string): Promise<void> => {
    await api.delete(`/admins/${id}`);
  },
};