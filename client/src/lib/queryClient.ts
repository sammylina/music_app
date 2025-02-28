
import { QueryClient, QueryFunction } from "@tanstack/react-query";

async function throwIfResNotOk(res: Response) {
  if (!res.ok) {
    const text = (await res.text()) || res.statusText;
    throw new Error(`${res.status}: ${text}`);
  }
}

export async function apiRequest(
  method: string,
  url: string,
  data?: unknown | undefined,
): Promise<Response> {
  const res = await fetch(url, {
    method,
    headers: data ? { "Content-Type": "application/json" } : {},
    body: data ? JSON.stringify(data) : undefined,
    credentials: "include",
  });

  await throwIfResNotOk(res);
  return res;
}

type UnauthorizedBehavior = "returnNull" | "throw";
export const getQueryFn: <T>(options: {
  on401: UnauthorizedBehavior;
}) => QueryFunction<T> =
  ({ on401: unauthorizedBehavior }) =>
  async ({ queryKey }) => {
    const res = await fetch(queryKey[0] as string, {
      credentials: "include",
    });

    if (unauthorizedBehavior === "returnNull" && res.status === 401) {
      return null;
    }

    await throwIfResNotOk(res);
    return await res.json();
  };

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryFn: getQueryFn({ on401: "throw" }),
      refetchInterval: false,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
      retry: false,
    },
    mutations: {
      retry: false,
    },
  },
});

// Utility functions for Flask backend
import config from '../config';

export const apiRequest = async (method: string, url: string, data?: any) => {
  const fullUrl = url.startsWith('http') ? url : `${config.apiUrl}${url}`;
  console.log(`Making ${method} request to: ${fullUrl}`);

  const options: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(fullUrl, options);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'An error occurred' }));
    throw new Error(errorData.error || errorData.message || 'Request failed');
  }
  
  return response;
};

export const loginUser = async (username: string, password: string) => {
  const res = await apiRequest('POST', '/api/login', { username, password });
  return res.json();
};

export const registerUser = async (username: string, password: string) => {
  const res = await apiRequest('POST', '/api/register', { username, password });
  return res.json();
};

export const logoutUser = async () => {
  await apiRequest('POST', '/api/logout', {});
};

export const getCurrentUser = async () => {
  try {
    const res = await fetch('/api/user', { credentials: 'include' });
    if (!res.ok) {
      if (res.status === 401) return null;
      throw new Error('Failed to get current user');
    }
    return res.json();
  } catch (error) {
    return null;
  }
};

export const getPlaylists = async () => {
  const res = await fetch('/api/playlists', { credentials: 'include' });
  await throwIfResNotOk(res);
  return res.json();
};

export const getPlaylistSongs = async (playlistId: number) => {
  const res = await fetch(`/api/playlists/${playlistId}/songs`, { credentials: 'include' });
  await throwIfResNotOk(res);
  return res.json();
};

