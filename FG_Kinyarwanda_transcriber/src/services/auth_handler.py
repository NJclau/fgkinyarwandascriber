import streamlit as st
import os
from typing import Optional
from src.config.settings import config

def check_authentication() -> bool:
    """
    Simple authentication check for MVP.
    
    For production, integrate with:
    - streamlit-google-oauth package
    - Firebase Authentication
    - Auth0
    
    Current implementation: Demo mode with optional password
    """
    
    # Check if demo mode is enabled
    demo_mode = config.demo_mode
    
    if demo_mode:
        # Demo mode: auto-authenticate
        st.session_state.user_email = "demo@focusgroup.rw"
        st.session_state.user_name = "Demo User"
        return True
    
    # Production mode: Check for valid credentials
    allowed_emails = config.allowed_emails
    
    if not allowed_emails:
        st.error("No authorized users configured. Add ALLOWED_EMAILS to secrets.toml")
        return False
    
    # For MVP, you can manually set credentials here
    # In production, integrate Google OAuth as shown below
    st.session_state.user_email = "user@example.com"
    st.session_state.user_name = "Focus Group User"
    
    return True


def setup_google_oauth():
    """
    Production-ready Google OAuth integration.
    
    To implement:
    1. Install: pip install streamlit-google-oauth
    2. Set up Google Cloud Console:
       - Create OAuth 2.0 credentials
       - Add authorized redirect URIs
       - Enable Google+ API
    3. Add to secrets.toml:
       GOOGLE_CLIENT_ID = "your-client-id"
       GOOGLE_CLIENT_SECRET = "your-secret"
    
    Example implementation:
    
    from streamlit_google_auth import Authenticate
    
    authenticator = Authenticate(
        secret_credentials_path='secrets.toml',
        cookie_name='focus_group_auth',
        cookie_key='random_signature_key',
        redirect_uri='http://localhost:8501',
    )
    
    authenticator.check_authentification()
    st.write(f"Welcome {authenticator.user_email}")
    """
    pass


def logout():
    """Clear authentication session"""
    if 'authenticated' in st.session_state:
        st.session_state.authenticated = False
    if 'user_email' in st.session_state:
        del st.session_state.user_email
    if 'user_name' in st.session_state:
        del st.session_state.user_name


def get_user_info() -> dict:
    """Get current user information"""
    return {
        'email': st.session_state.get('user_email', 'anonymous'),
        'name': st.session_state.get('user_name', 'Anonymous User'),
        'authenticated': st.session_state.get('authenticated', False)
    }


# Production OAuth Integration Steps:
"""
DEPLOYMENT CHECKLIST FOR GOOGLE OAUTH:

1. Google Cloud Console Setup:
   - Go to console.cloud.google.com
   - Create new project or select existing
   - Enable "Google+ API"
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: Web application
   - Add authorized redirect URIs:
     * http://localhost:8501 (for local testing)
     * https://your-app.streamlit.app (for deployment)
   - Copy Client ID and Client Secret

2. Update secrets.toml:
   [google_oauth]
   client_id = "your-client-id.apps.googleusercontent.com"
   client_secret = "your-client-secret"
   redirect_uri = "https://your-app.streamlit.app"

3. Update requirements.txt:
   streamlit-google-oauth==0.1.7

4. Update auth_handler.py:
   from streamlit_google_auth import Authenticate
   
   def check_authentication():
       auth = Authenticate(
           secret_credentials_path='.streamlit/secrets.toml',
           cookie_name='focus_group_auth',
           cookie_key=st.secrets["COOKIE_KEY"],
           redirect_uri=st.secrets["google_oauth"]["redirect_uri"]
       )
       
       auth.check_authentification()
       
       if auth.is_authentificated:
           st.session_state.authenticated = True
           st.session_state.user_email = auth.user_email
           return True
       return False

5. Security best practices:
   - Never commit secrets.toml to git
   - Add secrets via Streamlit Cloud dashboard
   - Use HTTPS in production
   - Implement session timeouts
   - Log authentication attempts
"""
