// main.js - Common script for logged-in pages and shared functionality

document.addEventListener('DOMContentLoaded', () => {
    // Only run these functions on protected pages (not on login or register)
    if (!window.location.pathname.includes('/page/login') && !window.location.pathname.includes('/page/register')) {
        checkAuthStatus();
        loadProfile();
    }

    document.getElementById('logout-btn')?.addEventListener('click', async () => {
        try {
            const response = await fetch('/auth/logout', { method: 'POST' });
            if (response.ok) {
                window.location.href = '/page/login';
            }
        } catch (error) {
            showAlert('Error logging out', 'error');
        }
    });

    // Attach the generic form submission handler only on protected pages
    if (!window.location.pathname.includes('/page/login') && !window.location.pathname.includes('/page/register')) {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                // Use the action attribute if set; otherwise, use data-action.
                const action = form.getAttribute('action') || form.dataset.action;
                // Use custom data-method if defined; otherwise, default to form.method.
                const method = form.dataset.method ? form.dataset.method.toUpperCase() : form.method.toUpperCase();
                
                // Properly handle PUT requests
                if (method === 'PUT') {
                    try {
                        // Convert FormData to URLSearchParams for PUT
                        const params = new URLSearchParams();
                        for (const pair of formData.entries()) {
                            params.append(pair[0], pair[1]);
                        }
                        
                        const response = await fetch(action, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded'
                            },
                            body: params.toString()
                        });
                        
                        const data = await response.json();
                        if (response.ok) {
                            // Refresh profile data if the update profile form was submitted
                            if (action === '/user/update') {
                                loadProfile();
                            }
                            if (data.redirect) {
                                window.location.href = data.redirect;
                            } else {
                                showAlert(data.message || 'Operation successful', 'success');
                            }
                        } else {
                            showAlert(data.error || 'Something went wrong', 'error');
                        }
                    } catch (error) {
                        showAlert('Network error occurred', 'error');
                    }
                } else {
                    // Handle GET, POST, etc. normally
                    try {
                        const body = method === 'GET' ? null : formData;
                        const response = await fetch(action, {
                            method: method,
                            body: body
                        });
                        
                        const data = await response.json();
                        if (response.ok) {
                            // For registration, show modal and redirect (if applicable)
                            if (action === '/auth/register') {
                                const modal = document.getElementById('successModal');
                                modal.style.display = 'block';
                                
                                let seconds = 3;
                                const countdownEl = document.getElementById('countdown');
                                const countdownInterval = setInterval(() => {
                                    seconds--;
                                    countdownEl.textContent = seconds;
                                    if (seconds <= 0) {
                                        clearInterval(countdownInterval);
                                        window.location.href = '/page/login';
                                    }
                                }, 1000);
                            } else {
                                if (data.redirect) {
                                    window.location.href = data.redirect;
                                } else {
                                    showAlert(data.message || 'Operation successful', 'success');
                                }
                            }
                        } else {
                            showAlert(data.error || 'Something went wrong', 'error');
                        }
                    } catch (error) {
                        showAlert('Network error occurred', 'error');
                    }
                }
            });
        });
    }
});

/**
 * Fetch user profile data and populate the form fields.
 */
async function loadProfile() {
    try {
        const response = await fetch('/user/profile');
        const data = await response.json();

        if (response.ok && data.profile) {
            // Make sure these IDs match the HTML inputs or elements
            const usernameEl = document.getElementById('username');
            const creditsEl = document.getElementById('credits');
            const phoneEl = document.getElementById('phone');
            const firstNameEl = document.getElementById('first_name');
            const lastNameEl = document.getElementById('last_name');
            const dobEl = document.getElementById('dob');
            
            if (usernameEl) {
                if (usernameEl.tagName === 'INPUT') {
                    usernameEl.value = data.profile.username || '';
                } else {
                    usernameEl.textContent = data.profile.username || '';
                }
            }
            
            if (creditsEl) creditsEl.textContent = data.profile.credits || '0';
            if (phoneEl) phoneEl.value = data.profile.phone || '';
            if (firstNameEl) firstNameEl.value = data.profile.first_name || '';
            if (lastNameEl) lastNameEl.value = data.profile.last_name || '';
            if (dobEl) dobEl.value = data.profile.dob || '';
        }
    } catch (error) {
        showAlert('Failed to load profile', 'error');
    }
}

/**
 * Check if the user is authenticated on protected pages.
 */
function checkAuthStatus() {
    const protectedPages = ['profile', 'upload', 'matches', 'credits'];
    const currentPage = window.location.pathname.split('/').pop();
    if (protectedPages.includes(currentPage) && !localStorage.getItem('username')) {
        window.location.href = '/page/login';
    }
}

/**
 * Display alert messages for user feedback.
 */
function showAlert(message, type = 'success') {
    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${type === 'error' ? 'error' : 'success'}`;
    alertEl.textContent = message;
    document.body.prepend(alertEl);
    setTimeout(() => alertEl.remove(), 3000);
}

/**
 * (Optional) Preview file selection, if used elsewhere in your app.
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    const preview = document.getElementById('preview');
    if (file && preview) {
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
    }
}

/**
 * Function to load matches (if this feature is used on another page).
 */
async function loadMatches() {
    try {
        const pathParts = window.location.pathname.split('/');
        const docId = pathParts[pathParts.length - 1];
        const response = await fetch(`/matches/${docId}`);
        const data = await response.json();
        if (response.ok) {
            const matchesList = document.getElementById('matches-list');
            if (matchesList) {
                matchesList.innerHTML = data.matches.map(match => `
                    <div class="match-card ${match.is_similar ? 'similar' : 'unique'}">
                        <h4>${match.filename}</h4>
                        <p>Similarity: ${match.similarity * 100}%</p>
                        <p>Status: ${match.is_similar ? 'Similar' : 'Not Similar'}</p>
                    </div>
                `).join('');
            }
        } else {
            showAlert('Failed to load matches', 'error');
        }
    } catch (error) {
        console.error('Error loading matches:', error);
        showAlert('Network error occurred', 'error');
    }
}
