import pytest
import sys
from pathlib import Path
from flask import session, url_for, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
from flask_app.models import User
from flask_app.auth import auth_bp

# Add parent directory to Python path to find the flask-app package
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def test_login_page(client):
    """Test login page loads"""
    response = client.get('/login')
    assert response.status_code == 200
    assert 'iniciar sesion'.encode('utf-8') in response.data.lower()

def test_login_success(client, test_user):
    """Test successful login"""
    with client:  # Esto mantiene el contexto de la sesión
        response = client.post('/login', data={
            'email': test_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'user_id' in session
        assert session['user_id'] == test_user.id

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/login', data={
        'email': 'wrong@email.com',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert 'credenciales inválidas'.encode('utf-8') in response.data.lower()

def test_register_page(client):
    """Test register page loads"""
    response = client.get('/register')
    assert response.status_code == 200
    assert 'registro'.encode('utf-8') in response.data.lower()

def test_register_success(client, app):
    """Test successful registration"""
    with client:  # Esto mantiene el contexto de la sesión
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'registro exitoso'.encode('utf-8') in response.data.lower()
        
        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(email='newuser@test.com').first()
            assert user is not None
            assert user.username == 'newuser'

def test_register_duplicate_email(client, test_user):
    """Test registration with existing email"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': test_user.email,
        'password': 'password123'
    }, follow_redirects=True)
    assert 'el email ya existe'.encode('utf-8') in response.data.lower()

def test_logout(client, test_user):
    """Test logout functionality"""
    with client:  # Esto mantiene el contexto de la sesión
        # First login
        client.post('/login', data={
            'email': test_user.email,
            'password': 'password123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert 'has cerrado sesión'.encode('utf-8') in response.data.lower()
        assert 'user_id' not in session 