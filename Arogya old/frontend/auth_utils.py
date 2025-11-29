"""
Frontend Authentication Utilities
"""

import functools
from flask import request, redirect, url_for, session, jsonify

def login_required(f):
    """Decorator to require login for routes"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for access token in localStorage (sent via headers)
        token = request.headers.get('Authorization')
        if not token:
            # Check session as fallback
            if 'access_token' not in session:
                return redirect(url_for('login'))
            token = f"Bearer {session['access_token']}"
        
        # Verify token with backend
        try:
            import requests
            headers = {'Authorization': token}
            response = requests.get('http://localhost:5000/auth/me', headers=headers, timeout=5)
            
            if response.status_code != 200:
                # Token invalid, clear session and redirect
                session.pop('access_token', None)
                session.pop('user', None)
                return redirect(url_for('login'))
                
        except Exception:
            # Backend unavailable, clear session and redirect
            session.pop('access_token', None)
            session.pop('user', None)
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user from session or request headers"""
    token = request.headers.get('Authorization')
    if not token:
        token = f"Bearer {session.get('access_token', '')}"
    
    try:
        import requests
        headers = {'Authorization': token}
        response = requests.get('http://localhost:5000/auth/me', headers=headers, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def logout_user():
    """Logout user and clear session"""
    token = request.headers.get('Authorization')
    if not token:
        token = f"Bearer {session.get('access_token', '')}"
    
    try:
        import requests
        headers = {'Authorization': token}
        requests.post('http://localhost:5000/auth/logout', headers=headers, timeout=5)
    except Exception:
        pass  # Continue with local logout even if backend call fails
    
    # Clear local session
    session.pop('access_token', None)
    session.pop('user', None)
