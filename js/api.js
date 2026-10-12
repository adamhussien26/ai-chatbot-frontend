/**
 * ==========================================================================
 * api.js — عميل REST API لربط الواجهة الحالية بالـ Backend (FastAPI)
 * لا يغيّر أي تصميم: طبقة اتصال فقط مع تراجع تلقائي (fallback) للوضع التجريبي
 * عندما يكون الخادم غير متاح، حتى تظل الشاشات تعمل كما هي.
 * ==========================================================================
 */

const API = (() => {
  // عنوان الـ Backend — يمكن تغييره عبر localStorage أو تعديل هذا السطر
  const BASE = localStorage.getItem('ust_api_base') || 'http://localhost:8000/api';
  const TOKEN_KEY = 'ust_token';
  const USER_KEY = 'ust_user';

  let backendAvailable = null; // null = لم يُفحص بعد

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function setSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  function getUser() {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY) || 'null');
    } catch (e) {
      return null;
    }
  }

  function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  async function request(method, path, body, options = {}) {
    const headers = {};
    if (!(body instanceof FormData) && body !== undefined) {
      headers['Content-Type'] = 'application/json';
    }
    const token = getToken();
    if (token) headers['Authorization'] = 'Bearer ' + token;

    const res = await fetch(BASE + path, {
      method,
      headers,
      body: body === undefined ? undefined : (body instanceof FormData ? body : JSON.stringify(body)),
      signal: options.timeout ? AbortSignal.timeout(options.timeout) : undefined,
    });

    let data = null;
    try { data = await res.json(); } catch (e) { /* استجابة بدون JSON */ }

    if (!res.ok) {
      const err = new Error((data && data.error && data.error.message) || 'حدث خطأ في الخادم.');
      err.status = res.status;
      err.data = data;
      throw err;
    }
    backendAvailable = true;
    return data;
  }

  /** فحص توفر الخادم (مع مهلة قصيرة حتى لا تعلق الواجهة) */
  async function isAvailable() {
    if (backendAvailable !== null) return backendAvailable;
    try {
      const res = await fetch(BASE + '/health', { signal: AbortSignal.timeout(2500) });
      backendAvailable = res.ok;
    } catch (e) {
      backendAvailable = false;
    }
    return backendAvailable;
  }

  return {
    BASE,
    getToken,
    setSession,
    getUser,
    clearSession,
    isAvailable,

    get: (path, opts) => request('GET', path, undefined, opts),
    post: (path, body, opts) => request('POST', path, body, opts),
    put: (path, body, opts) => request('PUT', path, body, opts),
    patch: (path, body, opts) => request('PATCH', path, body, opts),
    del: (path, opts) => request('DELETE', path, undefined, opts),

    /** هل الخطأ سببه انقطاع الشبكة (لتفعيل الوضع التجريبي)؟ */
    isNetworkError(err) {
      return err instanceof TypeError || err.status === undefined;
    },
  };
})();
