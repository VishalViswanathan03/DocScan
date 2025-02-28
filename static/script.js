async function postData(url, data) {
    const response = await fetch(url, {
      method: 'POST',
      body: data
    });
    return await response.json();
  }
  
  async function getData(url) {
    const response = await fetch(url);
    return await response.json();
  }
  
  async function handleLogin(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const result = await postData('/auth/login', formData);
    if (result.success) {
      alert('Login successful!');
      window.location.href = '/page/profile'; 
    } else {
      alert(result.error || 'Login failed');
    }
  }
  
  async function handleRegister(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const result = await postData('/auth/register', formData);
    if (result.success) {
      alert('Registration successful!');
      window.location.href = '/page/login';
    } else {
      alert(result.error || 'Registration failed');
    }
  }
  
  async function handleLogout() {
    const result = await postData('/auth/logout', new FormData());
    if (result.success) {
      alert('Logged out!');
      window.location.href = '/page/index';
    } else {
      alert('Logout failed');
    }
  }
  
  async function handleUpload(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const result = await postData('/upload', formData);
    if (result.message) {
      alert(result.message);
    } else {
      alert('Upload failed');
    }
  }
  
  async function loadProfile() {
    const profile = await getData('/user/profile');
    if (profile.error) {
      alert(profile.error);
      window.location.href = '/page/login';
    } else {
      document.getElementById('profileUsername').innerText = profile.profile.username;
      document.getElementById('profileCredits').innerText = profile.profile.credits;
    }
  }
  
  async function loadAnalytics() {
    const analytics = await getData('/admin/analytics');
    if (analytics.error) {
      alert(analytics.error);
      window.location.href = '/page/index';
    } else {
      document.getElementById('totalScans').innerText = analytics.total_scans;
      const topUsersUl = document.getElementById('topUsers');
      analytics.top_users.forEach(([user, scans]) => {
        const li = document.createElement('li');
        li.textContent = `${user} - ${scans} scans`;
        topUsersUl.appendChild(li);
      });
    }
  }
  