import axios from 'axios';

const STORAGE_KEY = 'macrosentiment_api_url';
const BUILD_URL = import.meta.env.VITE_API_URL || '';

// If the build shipped a new API URL, clear any stale localStorage override
// so the fresh tunnel URL takes effect automatically on deploy.
if (BUILD_URL) {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored && stored !== BUILD_URL) {
    localStorage.removeItem(STORAGE_KEY);
  }
}

export function getApiUrl(): string {
  return localStorage.getItem(STORAGE_KEY)
    || BUILD_URL
    || 'http://localhost:8002';
}

export function setApiUrl(url: string) {
  const cleaned = url.replace(/\/+$/, '');
  if (cleaned) {
    localStorage.setItem(STORAGE_KEY, cleaned);
  } else {
    localStorage.removeItem(STORAGE_KEY);
  }
  api.defaults.baseURL = `${getApiUrl()}/api`;
}

export const api = axios.create({
  baseURL: `${getApiUrl()}/api`,
  timeout: 30000,
});
