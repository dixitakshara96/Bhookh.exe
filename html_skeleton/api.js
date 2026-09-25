/**
 * API Client Layer for Bhookh
 * Matches endpoints defined in docs/api-contract.md
 */

// 1. Base URL configuration
const BASE_URL = (typeof process !== 'undefined' && process.env && process.env.NEXT_PUBLIC_API_URL) 
    || (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) 
    || ''; // Defaults to same origin if not explicitly provided

// Token management
const TOKEN_KEY = 'bhookh_jwt_token';
const getToken = () => localStorage.getItem(TOKEN_KEY);
const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);
const clearToken = () => localStorage.removeItem(TOKEN_KEY);

// Custom Error Class
class ApiError extends Error {
    constructor(status, errorPayload) {
        super(errorPayload.message || 'An API error occurred');
        this.status = status;
        this.code = errorPayload.code;
        this.fields = errorPayload.fields || {};
        this.name = 'ApiError';
    }
}

/**
 * Core fetch wrapper that handles timeouts, JWT attachment, and unified error handling
 */
async function fetchWithTimeout(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    
    // Set up 20-second timeout with friendly message
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000);
    
    // Set headers and attach JWT
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers,
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // Handle 401 Unauthorized globally
        if (response.status === 401) {
            clearToken();
            if (typeof window !== 'undefined' && !window.location.pathname.includes('/login.html')) {
                window.location.href = 'login.html'; // Adjust redirect path as needed
            }
        }

        // Parse JSON response
        const data = await response.json().catch(() => null);

        // Handle error envelope mapping
        if (!response.ok) {
            if (data && data.error) {
                throw new ApiError(response.status, data.error);
            }
            throw new ApiError(response.status, {
                code: 'UNKNOWN_ERROR',
                message: 'An unexpected error occurred.',
                fields: {}
            });
        }

        return data; // Return the full success envelope ({ data, message })
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new ApiError(408, {
                code: 'TIMEOUT',
                message: 'The server is waking up or experiencing high traffic. Please try again.',
                fields: {}
            });
        }
        throw error;
    }
}

// Utility to serialize query params
const serializeQueryParams = (params) => {
    if (!params || Object.keys(params).length === 0) return '';
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && value !== '') {
            searchParams.append(key, value);
        }
    }
    const queryStr = searchParams.toString();
    return queryStr ? `?${queryStr}` : '';
};

export const API = {
    // ----------------------------
    // 1. Authentication Endpoints
    // ----------------------------
    
    register: async (name, email, password) => {
        const response = await fetchWithTimeout('/api/v1/auth/register', {
            method: 'POST',
            body: JSON.stringify({ name, email, password })
        });
        if (response.data?.token) setToken(response.data.token);
        return response;
    },

    login: async (email, password) => {
        const response = await fetchWithTimeout('/api/v1/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        if (response.data?.token) setToken(response.data.token);
        return response;
    },

    getCurrentUser: async () => {
        return fetchWithTimeout('/api/v1/auth/me', {
            method: 'GET'
        });
    },

    logout: async () => {
        const response = await fetchWithTimeout('/api/v1/auth/logout', {
            method: 'DELETE'
        });
        clearToken();
        return response;
    },

    // ----------------------------
    // 2. Dishes Endpoints
    // ----------------------------
    
    getDishes: async (params = {}) => {
        // params: { q, diet, include, exclude, spice, price_max, area, page, limit }
        const query = serializeQueryParams(params);
        return fetchWithTimeout(`/api/v1/dishes${query}`, {
            method: 'GET'
        });
    },

    getDishDetails: async (dishId) => {
        return fetchWithTimeout(`/api/v1/dishes/${dishId}`, {
            method: 'GET'
        });
    },

    // ----------------------------
    // 3. Reviews Endpoints
    // ----------------------------
    
    getDishReviews: async (dishId, params = {}) => {
        // params: { page, limit }
        const query = serializeQueryParams(params);
        return fetchWithTimeout(`/api/v1/dishes/${dishId}/reviews${query}`, {
            method: 'GET'
        });
    },

    addDishReview: async (dishId, reviewData) => {
        // reviewData: { rating, comment, spice_feedback, taste_feedback, portion_feedback }
        return fetchWithTimeout(`/api/v1/dishes/${dishId}/reviews`, {
            method: 'POST',
            body: JSON.stringify(reviewData)
        });
    },

    // ----------------------------
    // 4. Favourites Endpoints
    // ----------------------------
    
    getMyFavourites: async (params = {}) => {
        // params: { page, limit }
        const query = serializeQueryParams(params);
        return fetchWithTimeout(`/api/v1/me/favourites${query}`, {
            method: 'GET'
        });
    },

    addToFavourites: async (dishId) => {
        return fetchWithTimeout('/api/v1/me/favourites', {
            method: 'POST',
            body: JSON.stringify({ dish_id: dishId })
        });
    },

    removeFromFavourites: async (dishId) => {
        return fetchWithTimeout(`/api/v1/me/favourites/${dishId}`, {
            method: 'DELETE'
        });
    },

    // ----------------------------
    // 5. Metadata Endpoints
    // ----------------------------
    
    getCategories: async (params = {}) => {
        // params: { page, limit }
        const query = serializeQueryParams(params);
        return fetchWithTimeout(`/api/v1/categories${query}`, {
            method: 'GET'
        });
    }
};
