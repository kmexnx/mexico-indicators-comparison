import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for potential JWT auth
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Cities endpoints
export const fetchCities = async (filters = {}) => {
  const { data } = await apiClient.get('/cities', { params: filters });
  return data;
};

export const fetchCityById = async (id) => {
  const { data } = await apiClient.get(`/cities/${id}`);
  return data;
};

export const searchCitiesByName = async (name, state = null) => {
  const params = { name };
  if (state) params.state = state;
  
  const { data } = await apiClient.get(`/cities/by-name/${name}`, { params });
  return data;
};

// Indicators endpoints
export const fetchIndicators = async (category = null) => {
  const params = category ? { category } : {};
  const { data } = await apiClient.get('/indicators', { params });
  return data;
};

export const fetchIndicatorById = async (id) => {
  const { data } = await apiClient.get(`/indicators/${id}`);
  return data;
};

// Health indicators endpoints
export const fetchHealthIndicators = async (cityId = null, year = null) => {
  const params = {};
  if (cityId) params.city_id = cityId;
  if (year) params.year = year;
  
  const { data } = await apiClient.get('/health-indicators', { params });
  return data;
};

// Education indicators endpoints
export const fetchEducationIndicators = async (cityId = null, year = null) => {
  const params = {};
  if (cityId) params.city_id = cityId;
  if (year) params.year = year;
  
  const { data } = await apiClient.get('/education-indicators', { params });
  return data;
};

// Comparison endpoints
export const generateComparison = async (cityIds, indicatorIds, year = null) => {
  const payload = {
    city_ids: cityIds,
    indicator_ids: indicatorIds,
    year: year,
  };
  
  const { data } = await apiClient.post('/comparisons', payload);
  return data;
};

export const getComparisonCategories = async () => {
  const { data } = await apiClient.get('/comparisons/indicators');
  return data;
};

// Error handling wrapper
export const apiRequest = async (apiFunction, ...args) => {
  try {
    return await apiFunction(...args);
  } catch (error) {
    // Handle different types of errors
    if (error.response) {
      // Server responded with error status (4xx, 5xx)
      const errorMessage = error.response.data.detail || 'Error en el servidor';
      throw new Error(errorMessage);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('No se pudo conectar al servidor');
    } else {
      // Error setting up the request
      throw new Error('Error al procesar la solicitud');
    }
  }
};
