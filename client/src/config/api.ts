/**
 * API Configuration
 * Centralized configuration for API endpoints
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  health: `${API_BASE_URL}/api/health`,
  uploadFile: `${API_BASE_URL}/api/upload_file`,
  query: `${API_BASE_URL}/api/query`,
  listFiles: `${API_BASE_URL}/api/list_files`,
  deleteFile: `${API_BASE_URL}/api/delete_file`,
  getFileText: `${API_BASE_URL}/api/get_file_text`,
} as const;
