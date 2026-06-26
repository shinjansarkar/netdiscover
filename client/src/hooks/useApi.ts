import useSWR from 'swr';

// Use the environment variable for production, fallback to local for development
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000/api';

// For local testing, we hardcode the fallback key, but normally this would be process.env.NEXT_PUBLIC_API_KEY
export const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "dev_secret_key";

export const apiFetch = async (url: string, options: RequestInit = {}) => {
  const headers = {
    ...options.headers,
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  };
  const res = await fetch(`${API_BASE}${url}`, { ...options, headers });
  if (!res.ok) throw new Error("API request failed");
  return res.json();
};

export const fetcher = (url: string) => apiFetch(url);

export function useDashboard() {
  return useSWR('/dashboard', fetcher);
}

export function useScans() {
  return useSWR('/scans', fetcher);
}

export function useScanDetails(scanId: string | null) {
  return useSWR(scanId ? `/scans/${scanId}` : null, fetcher);
}

export function useReportContent(scanId: string | null) {
  return useSWR(scanId ? `/reports/${scanId}/content` : null, fetcher);
}

export function useLogs() {
  return useSWR('/logs', fetcher);
}
