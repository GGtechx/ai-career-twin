/**
 * API Client Service for AI Digital Career Twin
 * Handles authentication tokens, request headers, and backend endpoints.
 */

const API_BASE_URL = ''; // Relative URL handled by Vite dev server proxy

export const TOKEN_KEY = 'career_twin_token';
export const USER_KEY = 'career_twin_user';

export const getToken = () => localStorage.getItem(TOKEN_KEY);

export const getUser = () => {
  const userStr = localStorage.getItem(USER_KEY);
  try {
    return userStr ? JSON.parse(userStr) : null;
  } catch (e) {
    return null;
  }
};

export const setAuthSession = (token, user) => {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const clearAuthSession = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

export const isAuthenticated = () => {
  const token = getToken();
  return !!token;
};

async function apiRequest(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers
  };

  try {
    const response = await fetch(endpoint, config);

    if (response.status === 401) {
      // Unauthorized or token expired
      clearAuthSession();
      // Only redirect if not already on login or register
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        window.location.href = '/login';
      }
    }

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.detail || (Array.isArray(data.detail) ? data.detail[0]?.msg : null) || 'Request failed';
      throw new Error(errorMsg);
    }

    return data;
  } catch (err) {
    throw err;
  }
}

export const authAPI = {
  login: async (email, password) => {
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (data.access_token && data.user) {
      setAuthSession(data.access_token, data.user);
    }
    return data;
  },

  register: async (userData) => {
    const data = await apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
    if (data.access_token && data.user) {
      setAuthSession(data.access_token, data.user);
    }
    return data;
  },

  logout: async () => {
    try {
      await apiRequest('/auth/logout', { method: 'POST' });
    } catch (e) {
      // ignore
    } finally {
      clearAuthSession();
    }
  },

  getMe: async () => {
    return apiRequest('/auth/me');
  }
};

export const profileAPI = {
  getProfile: async () => {
    return apiRequest('/profile/me');
  },

  updateProfile: async (profileData) => {
    return apiRequest('/profile/me', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
  }
};

export const systemAPI = {
  getHealth: async () => {
    return apiRequest('/api/health');
  },
  getDbInfo: async () => {
    return apiRequest('/api/health/db');
  }
};

export const resumeAPI = {
  uploadResume: async (file) => {
    const token = getToken();
    const formData = new FormData();
    formData.append('file', file);

    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch('/resume/upload', {
      method: 'POST',
      headers,
      body: formData
    });

    if (response.status === 401) {
      clearAuthSession();
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        window.location.href = '/login';
      }
    }

    const data = await response.json();
    if (!response.ok) {
      const errorMsg = data.detail || (Array.isArray(data.detail) ? data.detail[0]?.msg : null) || 'Upload failed';
      throw new Error(errorMsg);
    }
    return data;
  },

  getMyResume: async () => {
    return apiRequest('/resume/my-resume');
  },

  getAnalysis: async () => {
    return apiRequest('/resume/analysis');
  }
};

export const companyAPI = {
  getCompanies: async (search = '') => {
    const q = search ? `?search=${encodeURIComponent(search)}` : '';
    return apiRequest(`/companies${q}`);
  },
  getCompany: async (id) => {
    return apiRequest(`/companies/${id}`);
  }
};

export const jobAPI = {
  getJobs: async (companyId = null, domain = null) => {
    const params = new URLSearchParams();
    if (companyId) params.append('company_id', companyId);
    if (domain) params.append('domain', domain);
    const q = params.toString() ? `?${params.toString()}` : '';
    return apiRequest(`/jobs${q}`);
  },
  getJob: async (id) => {
    return apiRequest(`/jobs/${id}`);
  },
  getJobRequirements: async (id) => {
    return apiRequest(`/jobs/${id}/requirements`);
  },
  selectTargetJob: async (id) => {
    return apiRequest(`/jobs/${id}/select-target`, { method: 'POST' });
  },
  getMyTargetJob: async () => {
    return apiRequest('/career-target');
  }
};

export const careerTargetAPI = {
  getCareerTarget: async () => {
    return apiRequest('/career-target');
  },
  setCareerTarget: async ({ job_id, company_id }) => {
    return apiRequest('/career-target', {
      method: 'PUT',
      body: JSON.stringify({ job_id, company_id })
    });
  }
};

export const skillGapAPI = {
  analyzeSkillGap: async (jobRoleId) => {
    return apiRequest(`/skill-gap/analyze/${jobRoleId}`, { method: 'POST' });
  },
  getMyLatestSkillGap: async () => {
    return apiRequest('/skill-gap/latest');
  },
  getJobSkillGap: async (jobRoleId) => {
    return apiRequest(`/skill-gap/job/${jobRoleId}`);
  }
};

export const placementAPI = {
  predictPlacement: async () => {
    return apiRequest('/placement/predict', { method: 'POST' });
  },
  getMyPlacementReadiness: async () => {
    return apiRequest('/placement/latest');
  }
};

export const recommendationAPI = {
  getRecommendations: async () => {
    return apiRequest('/recommendations');
  },
  generateRecommendations: async (forceRefresh = false) => {
    const q = forceRefresh ? '?force_refresh=true' : '';
    return apiRequest(`/recommendations/generate${q}`, { method: 'POST' });
  },
  toggleComplete: async (recId, completed = true) => {
    return apiRequest(`/recommendations/${recId}/complete?completed=${completed}`, { method: 'PATCH' });
  },
  dismiss: async (recId) => {
    return apiRequest(`/recommendations/${recId}/dismiss`, { method: 'PATCH' });
  }
};

export const roadmapAPI = {
  getRoadmap: async () => {
    return apiRequest('/roadmap');
  },
  generateRoadmap: async (forceRefresh = false) => {
    const q = forceRefresh ? '?force_refresh=true' : '';
    return apiRequest(`/roadmap/generate${q}`, { method: 'POST' });
  },
  updateTask: async (taskId, payload) => {
    return apiRequest(`/roadmap/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    });
  }
};

export const aiAPI = {
  askCareerAssistant: async (question, chatHistory = []) => {
    return apiRequest('/ai/career-assistant', {
      method: 'POST',
      body: JSON.stringify({ question, chat_history: chatHistory })
    });
  },
  getPersonalizedRecommendations: async () => {
    return apiRequest('/ai/recommendations');
  },
  searchKnowledgeBase: async (query, category = null) => {
    const cat = category ? `&category=${encodeURIComponent(category)}` : '';
    return apiRequest(`/ai/knowledge-base/search?query=${encodeURIComponent(query)}${cat}`);
  }
};

export const twinAPI = {
  getState: async () => {
    return apiRequest('/twin/state');
  },
  sync: async (eventLabel = 'Manual Sync') => {
    return apiRequest(`/twin/sync?event_label=${encodeURIComponent(eventLabel)}`, {
      method: 'POST'
    });
  },
  simulate: async (payload) => {
    return apiRequest('/twin/simulate', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }
};

export const dashboardAPI = {
  getSummary: async () => {
    return apiRequest('/dashboard/summary');
  }
};



