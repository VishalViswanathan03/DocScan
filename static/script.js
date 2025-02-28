// scripts.js

// Utility for POSTing form data
async function postFormData(url, formElement) {
    const formData = new FormData(formElement);
    const response = await fetch(url, {
      method: 'POST',
      body: formData
    });
    return response.json();
  }
  
  // Handle Register
  async function handleRegister(e) {
    e.preventDefault();
    const result = await postFormData('/auth/register', e.target);
    if (result.success) {
      alert('Registration successful!');
      window.location.href = '/page/login';
    } else {
      alert(result.error || 'Registration failed');
    }
  }
  
  // Handle Login
  async function handleLogin(e) {
    e.preventDefault();
    const result = await postFormData('/auth/login', e.target);
    if (result.success) {
      alert('Login successful!');
      window.location.href = '/page/profile';
    } else {
      alert(result.error || 'Login failed');
    }
  }
  
  // Handle Logout
  async function handleLogout() {
    const resp = await fetch('/auth/logout', { method: 'POST' });
    const data = await resp.json();
    if (data.success) {
      alert('Logged out!');
      window.location.href = '/page/index';
    } else {
      alert('Logout failed');
    }
  }
  
  // Load Profile
  async function loadProfile() {
    const resp = await fetch('/user/profile');
    const data = await resp.json();
    if (data.error) {
      alert(data.error);
      window.location.href = '/page/login';
    } else {
      document.getElementById('usernameField').textContent = data.profile.username;
      document.getElementById('creditsField').textContent = data.profile.credits;
    }
  }
  
  // Upload Document
  async function handleUpload(e) {
    e.preventDefault();
    const result = await postFormData('/upload', e.target);
    if (result.message) {
      alert(result.message);
    } else {
      alert('Upload failed');
    }
  }
  
  // Load Admin Analytics
  async function loadAnalytics() {
    const resp = await fetch('/admin/analytics');
    const data = await resp.json();
    if (data.error) {
      alert(data.error);
      window.location.href = '/page/index';
    } else {
      document.getElementById('totalScans').textContent = data.total_scans;
      const ul = document.getElementById('topUsers');
      data.top_users.forEach(([user, scans]) => {
        const li = document.createElement('li');
        li.textContent = `${user} - ${scans} scans`;
        ul.appendChild(li);
      });
    }
  }
  
  async function putFormData(url, formElement) {
    const formData = new FormData(formElement);
    const response = await fetch(url, {
      method: 'PUT',
      body: formData
    });
    return response.json();
  }
  
  async function handleUserUpdate(e) {
    e.preventDefault();
    const result = await putFormData('/user/update', e.target);
    if (result.message) {
      alert(result.message);
    } else {
      alert(result.error || 'Update failed');
    }
  }