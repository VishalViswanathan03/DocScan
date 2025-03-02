import pytest
from app import app
from flask import session
import time

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_register(client, mocker):
    unique_username = f"testuser_{int(time.time())}"
    mocker.patch('utils.auth.register_user', return_value=({"message": "User registered successfully"}, 201))
   
    response = client.post('/auth/register', data={
        'username': unique_username,
        'password': 'testpass'
    })
   
    print(response.json)
    assert response.status_code == 201
    assert response.json['message'] == "User registered successfully"

def test_login(client, mocker):
    mocker.patch('utils.auth.login_user', return_value=({"message": "Login successful", "role": "user"}, 200))
    
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['role'] = 'user'
    
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    assert response.status_code == 200

def test_profile_not_logged_in(client):
    response = client.get('/user/profile')
    assert response.status_code == 401
    assert response.json['error'] == "Not logged in"

def test_logout(client):
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.post('/auth/logout')
    assert response.status_code == 200
    assert response.json['message'] == "Logged out"