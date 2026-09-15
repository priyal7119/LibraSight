import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000",
    headers: {
        "Content-Type": "application/json",
    },
});

// Helper to clean up empty/null/undefined query params
const cleanParams = (params = {}) => {
    const cleaned = {};
    Object.keys(params).forEach((key) => {
        const val = params[key];
        if (val !== null && val !== undefined && val !== "") {
            cleaned[key] = val;
        }
    });
    return cleaned;
};

// Dashboard APIs with filter support
export const getDashboardSummary = (params = {}) =>
    API.get("/dashboard/summary", { params: cleanParams(params) });

export const getDashboardTrends = (params = {}) =>
    API.get("/dashboard/trends", { params: cleanParams(params) });

export const getDashboardStatus = (params = {}) =>
    API.get("/dashboard/status", { params: cleanParams(params) });

export const getDashboardAnalytics = (params = {}) =>
    API.get("/dashboard/analytics", { params: cleanParams(params) });

export const getFilterYears = () => API.get("/dashboard/years");
export const globalSearch = (q) => API.get("/dashboard/search", { params: { q } });

// Notifications API
export const getNotifications = () => API.get("/notifications");

// Books APIs
export const getBooks = (params = {}) => API.get("/books", { params: cleanParams(params) });
export const getTopBooks = () => API.get("/books/top");
export const getBookGenres = () => API.get("/books/genres");

// Readers APIs
export const getReaders = (params = {}) => API.get("/readers", { params: cleanParams(params) });
export const getReaderTypes = () => API.get("/readers/types");
export const getReaderActivity = () => API.get("/readers/activity");

// Branches APIs
export const getBranches = (params = {}) => API.get("/branches", { params: cleanParams(params) });
export const getBranchPerformance = () => API.get("/branches/performance");

// Collection APIs
export const getCollectionSummary = () => API.get("/collection/summary");

// Data Quality APIs
export const getDataQualitySummary = () => API.get("/data-quality/summary");
export const getRejectedRecords = () => API.get("/data-quality/rejected");

// Verified PDF Reports
export const downloadMonthlyPerformance = () =>
    API.get("/reports/monthly-performance", { responseType: "blob" });

export const downloadReadingTrends = () =>
    API.get("/reports/reading-trends", { responseType: "blob" });

export const downloadCollectionAnalysis = () =>
    API.get("/reports/collection-analysis", { responseType: "blob" });

export const downloadBranchPerformance = () =>
    API.get("/reports/branch-performance", { responseType: "blob" });

export const downloadDataQuality = () =>
    API.get("/reports/data-quality", { responseType: "blob" });

export default API;
