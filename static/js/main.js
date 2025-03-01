document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
    
    // Load existing profile data immediately on page load
    loadProfile();

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

    // Listen to all form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            // Use the action attribute if set; otherwise, use data-action.
            const action = form.getAttribute('action') || form.dataset.action;
            // Use custom data-method if defined; otherwise, default to form.method.
            const method = form.dataset.method ? form.dataset.method.toUpperCase() : form.method.toUpperCase();
            
            // If the method is PUT, convert FormData to URLSearchParams
            let body;
            if (method === 'PUT') {
                body = new URLSearchParams();
                for (const pair of formData.entries()) {
                    body.append(pair[0], pair[1]);
                }
            } else {
                body = method === 'GET' ? null : formData;
            }
            
            try {
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
                        setTimeout(() => {
                            window.location.href = '/page/login';
                        }, 3000);
                    } else {
                        // Refresh profile data if the update profile form was submitted
                        if (action === '/user/update') {
                            loadProfile();
                        }
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
        });
    });
});

/**
 * Fetch user profile data and populate the form fields.
 */
async function loadProfile() {
    try {
        const response = await fetch('/user/profile');
        const data = await response.json();

        // Make sure these IDs match the HTML inputs
        document.getElementById('username').textContent = data.profile.username;
        document.getElementById('credits').textContent = data.profile.credits;
        document.getElementById('phone').value = data.profile.phone || '';
        document.getElementById('first_name').value = data.profile.first_name || '';
        document.getElementById('last_name').value = data.profile.last_name || '';
        document.getElementById('dob').value = data.profile.dob || '';
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
    if (file) {
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
            matchesList.innerHTML = data.matches.map(match => `
                <div class="match-card ${match.is_similar ? 'similar' : 'unique'}">
                    <h4>${match.filename}</h4>
                    <p>Similarity: ${match.similarity * 100}%</p>
                    <p>Status: ${match.is_similar ? 'Similar' : 'Not Similar'}</p>
                </div>
            `).join('');
        } else {
            alert('Failed to load matches');
        }
    } catch (error) {
        console.error('Error loading matches:', error);
        alert('Network error occurred');
    }
}