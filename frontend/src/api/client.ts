import axios from 'axios';

const STORAGE_KEY = 'macrosentiment_api_url';

export function getApiUrl(): string {
  return localStorage.getItem(STORAGE_KEY)
    || import.meta.env.VITE_API_URL
    || 'http://localhost:8002';
}

export function setApiUrl(url: string) {
  const cleaned = url.replace(/\/+$/, '');
  if (cleaned) {
    localStorage.setItem(STORAGE_KEY, cleaned);
  } else {
    localStorage.removeItem(STORAGE_KEY);
  }
  // Update the axios instance
  api.defaults.baseURL = `${getApiUrl()}/api`;
}

export const api = axios.create({
  baseURL: `${getApiUrl()}/api`,
  timeout: 30000,
});
