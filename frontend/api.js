const API = 'https://skillbridge-backend-3na6.onrender.com';

function getToken() {
  return localStorage.getItem('token');
}

function getHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

function saveAnalysis(data) {
  localStorage.setItem('latest_analysis', JSON.stringify(data));
}

function getAnalysis() {
  const d = localStorage.getItem('latest_analysis');
  return d ? JSON.parse(d) : null;
}

function saveRoadmap(data) {
  localStorage.setItem('latest_roadmap', JSON.stringify(data));
}

function getRoadmap() {
  const d = localStorage.getItem('latest_roadmap');
  return d ? JSON.parse(d) : null;
}

function requireLogin() {
  if (!getToken()) {
    window.location.href = 'login.html';
    return false;
  }
  return true;
}

function logout() {
  localStorage.clear();
  window.location.href = 'login.html';
}

const AuthAPI = {
  async register(name, email, password) {
    const r = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    return r.json();
  },
  async login(email, password) {
    const r = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return r.json();
  },
  async me() {
    const r = await fetch(`${API}/auth/me`, { headers: getHeaders() });
    return r.json();
  }
};

const SkillsAPI = {
  async getRoles() {
    const r = await fetch(`${API}/skills/roles`);
    return r.json();
  },
  async getRoleSkills(roleId) {
    const r = await fetch(`${API}/skills/roles/${roleId}/skills`);
    return r.json();
  }
};

const AnalysisAPI = {
  async run(jobRole, skillRatings) {
    const r = await fetch(`${API}/analysis/run`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ job_role: jobRole, skill_ratings: skillRatings })
    });
    return r.json();
  },
  async getLatest() {
    const r = await fetch(`${API}/analysis/latest`, { headers: getHeaders() });
    return r.json();
  },
  async getHistory() {
    const r = await fetch(`${API}/analysis/history`, { headers: getHeaders() });
    return r.json();
  }
};

const RoadmapAPI = {
  async generate(analysisId, jobRole, skills) {
    const r = await fetch(`${API}/roadmap/generate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ analysis_id: analysisId, job_role: jobRole, skills })
    });
    return r.json();
  },
  async getLatest() {
    const r = await fetch(`${API}/roadmap/latest`, { headers: getHeaders() });
    return r.json();
  },
  async toggleTask(taskId) {
    const r = await fetch(`${API}/roadmap/task/${taskId}/complete`, {
      method: 'PATCH',
      headers: getHeaders()
    });
    return r.json();
  }
};

const DashboardAPI = {
  async getStats() {
    const r = await fetch(`${API}/dashboard/stats`, { headers: getHeaders() });
    return r.json();
  }
};

const ProfileAPI = {
  async get() {
    const r = await fetch(`${API}/profile/`, { headers: getHeaders() });
    return r.json();
  },
  async update(name, bio) {
    const r = await fetch(`${API}/profile/update`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ name, bio })
    });
    return r.json();
  }
};
