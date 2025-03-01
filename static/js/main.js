document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
    
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

    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const action = form.getAttribute('action') || form.dataset.action;
            
            try {
                const response = await fetch(action, {
                    method: form.method,
                    body: form.method === 'GET' ? null : formData
                });
                
                const data = await response.json();
                if (response.ok) {
                    if (action === '/auth/register') {
                        // Show success modal
                        const modal = document.getElementById('successModal');
                        modal.style.display = 'block';
                        
                        // Redirect after 3 seconds
                        setTimeout(() => {
                            window.location.href = '/page/login';
                        }, 3000);
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
        });
    });
});

function checkAuthStatus() {
    const protectedPages = ['profile', 'upload', 'matches', 'credits'];
    const currentPage = window.location.pathname.split('/').pop();
    
    if (protectedPages.includes(currentPage) && !localStorage.getItem('username')) {
        window.location.href = '/page/login';
    }
}

function showAlert(message, type = 'success') {
    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${type}`;
    alertEl.textContent = message;
    
    document.body.prepend(alertEl);
    setTimeout(() => alertEl.remove(), 3000);
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    const preview = document.getElementById('preview');
    
    if (file) {
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
    }
}

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