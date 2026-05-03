import axios from "axios";

const api = axios.create({
  baseURL: "/api/backend",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Response interceptor untuk error handling global
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ==================== STOCKS ====================
export const stocksApi = {
  getList: () => api.get("/api/stocks/list"),

  getAllQuotes: (tickers?: string) =>
    api.get("/api/stocks/quotes", { params: tickers ? { tickers } : {} }),

  getQuote: (ticker: string) =>
    api.get(`/api/stocks/${ticker}/quote`),

  getHistory: (ticker: string, period = "1y", interval = "1d") =>
    api.get(`/api/stocks/${ticker}/history`, { params: { period, interval } }),

  getInfo: (ticker: string) =>
    api.get(`/api/stocks/${ticker}/info`),

  getFinancials: (ticker: string) =>
    api.get(`/api/stocks/${ticker}/financials`),
};

// ==================== FOREX ====================
export const forexApi = {
  getPairs: () => api.get("/api/forex/pairs"),

  getAllRates: () => api.get("/api/forex/rates"),

  getHistory: (pair: string, period = "1y", interval = "1d") =>
    api.get("/api/forex/history", { params: { pair, period, interval } }),
};

// ==================== INDICES ====================
export const indicesApi = {
  getAll: () => api.get("/api/indices/"),

  getHistory: (code: string, period = "1y", interval = "1d") =>
    api.get(`/api/indices/${code}/history`, { params: { period, interval } }),
};

// ==================== NEWS ====================
export const newsApi = {
  getNews: (source = "all", limit = 20, goldFocus = true) =>
    api.get("/api/news/", { params: { source, limit, gold_focus: goldFocus } }),
};

// ==================== SCREENER ====================
export const screenerApi = {
  getSectors: () => api.get("/api/screener/sectors"),

  screener: (params: {
    sector?: string;
    min_market_cap?: number;
    max_pe?: number;
    min_roe?: number;
    sort_by?: string;
    order?: string;
    limit?: number;
  }) => api.get("/api/screener/", { params }),
};

// ==================== MACRO INDICATORS ====================
export const macroApi = {
  getSnapshot: () => api.get("/api/macro/snapshot"),

  getHistory: (seriesKey: string, period = "1mo", interval = "1d") =>
    api.get(`/api/macro/history/${seriesKey}`, { params: { period, interval } }),
};

// ==================== ECONOMIC CALENDAR ====================
export const economicCalendarApi = {
  getCalendar: () => api.get("/api/economic-calendar/calendar"),

  getLatest: () => api.get("/api/economic-calendar/latest"),
};

export default api;
