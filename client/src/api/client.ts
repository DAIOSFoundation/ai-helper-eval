import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
  },
});

// 요청 인터셉터
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      // 헤더 값을 안전하게 설정
      config.headers = config.headers || {};
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // 모든 헤더가 ISO-8859-1 호환인지 확인
    if (config.headers) {
      const safeHeaders: Record<string, string> = {};
      for (const [key, value] of Object.entries(config.headers)) {
        if (typeof value === 'string') {
          // 한글이 포함된 헤더 값을 인코딩
          try {
            // ISO-8859-1로 인코딩 가능한지 확인
            const encoded = encodeURIComponent(value);
            if (encoded === value || !/[^\x00-\xFF]/.test(value)) {
              safeHeaders[key] = value;
            } else {
              // 한글이 포함된 경우 base64로 인코딩
              safeHeaders[key] = btoa(unescape(encodeURIComponent(value)));
            }
          } catch (e) {
            // 인코딩 실패 시 원본 값 사용
            safeHeaders[key] = value;
          }
        } else {
          safeHeaders[key] = value;
        }
      }
      config.headers = safeHeaders;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
