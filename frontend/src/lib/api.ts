import axios from "axios";

// In production (Vercel): use /api/proxy to avoid HTTPS→HTTP mixed content browser block.
// The proxy strips /api/proxy and calls backend with /api/<path> — so we strip /api from paths.
// In development (localhost): talk directly to localhost:8000 with full /api paths.
const IS_PROD = process.env.NODE_ENV === "production";
const BASE_URL = IS_PROD
  ? "/api/proxy"
  : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

// Prefix to strip in production (proxy adds it back), keep full path in dev
const PROXY_STRIP = IS_PROD ? "/api" : "";

// Helper to build URL
function url(path: string) {
  return `${BASE_URL}${path.replace("/api", "")}`;
}

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
  // In production, axios paths don't need /api prefix since baseURL = /api/proxy
  // and we adjust individual calls below
});

// Response interceptor for error handling global
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ==================== STOCKS ====================
export const stocksApi = {
  getList: () => api.get(`${PROXY_STRIP}/stocks/list`),

  getAllQuotes: (tickers?: string) =>
    api.get(`${PROXY_STRIP}/stocks/quotes`, { params: tickers ? { tickers } : {} }),

  getQuote: (ticker: string) =>
    api.get(`${PROXY_STRIP}/stocks/${ticker}/quote`),

  getHistory: (ticker: string, period = "1y", interval = "1d") =>
    api.get(`${PROXY_STRIP}/stocks/${ticker}/history`, { params: { period, interval } }),

  getInfo: (ticker: string) =>
    api.get(`${PROXY_STRIP}/stocks/${ticker}/info`),

  getFinancials: (ticker: string) =>
    api.get(`${PROXY_STRIP}/stocks/${ticker}/financials`),
};

// ==================== FOREX ====================
export const forexApi = {
  getPairs: () => api.get(`${PROXY_STRIP}/forex/pairs`),

  getAllRates: () => api.get(`${PROXY_STRIP}/forex/rates`),

  getHistory: (pair: string, period = "1y", interval = "1d") =>
    api.get(`${PROXY_STRIP}/forex/history`, { params: { pair, period, interval } }),
};

// ==================== INDICES ====================
export const indicesApi = {
  getAll: () => api.get(`${PROXY_STRIP}/indices/`),

  getHistory: (code: string, period = "1y", interval = "1d") =>
    api.get(`${PROXY_STRIP}/indices/${code}/history`, { params: { period, interval } }),
};

// ==================== NEWS ====================
export const newsApi = {
  getNews: (source = "all", limit = 20, goldFocus = true) =>
    api.get(`${PROXY_STRIP}/news/`, { params: { source, limit, gold_focus: goldFocus } }),
};

// ==================== SCREENER ====================
export const screenerApi = {
  getSectors: () => api.get(`${PROXY_STRIP}/screener/sectors`),

  screener: (params: {
    sector?: string;
    min_market_cap?: number;
    max_pe?: number;
    min_roe?: number;
    sort_by?: string;
    order?: string;
    limit?: number;
  }) => api.get(`${PROXY_STRIP}/screener/`, { params }),
};

// ==================== MACRO INDICATORS ====================
export const macroApi = {
  getSnapshot: () => api.get(`${PROXY_STRIP}/macro/snapshot`),

  getHistory: (seriesKey: string, period = "1mo", interval = "1d") =>
    api.get(`${PROXY_STRIP}/macro/history/${seriesKey}`, { params: { period, interval } }),
};

// ==================== ECONOMIC CALENDAR ====================
export const economicCalendarApi = {
  getCalendar: () => api.get(`${PROXY_STRIP}/economic-calendar/calendar`),

  getLatest: () => api.get(`${PROXY_STRIP}/economic-calendar/latest`),
};

export default api;
