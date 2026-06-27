import useSWR from 'swr';

// Use the environment variable for production, fallback to local for development
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000/api';

export const apiFetch = async (url: string, options: RequestInit = {}) => {
  const headers = {
    ...options.headers,
    'Content-Type': 'application/json'
  };
  const res = await fetch(`${API_BASE}${url}`, { ...options, headers });
  if (!res.ok) throw new Error("API request failed");
  return res.json();
};

export const fetcher = (url: string) => apiFetch(url);

export function useDashboard(options?: any) {
  return useSWR('/dashboard', fetcher, options);
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

export function useLogs(options?: any) {
  return useSWR('/logs', fetcher, options);
}
