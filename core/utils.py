"""
Utility functions for the core app.
"""
import os
import logging

logger = logging.getLogger(__name__)


def validate_oauth_config():
    """
    Validate OAuth configuration and return status.
    Returns a dict with validation results.
    """
    result = {
        'google': {
            'client_id_set': False,
            'client_secret_set': False,
            'client_id_valid': False,
            'client_id_value': None,
            'issues': []
        },
        'github': {
            'client_id_set': False,
            'client_secret_set': False,
            'client_id_valid': False,
            'client_id_value': None,
            'issues': []
        }
    }
    
    # Check Google OAuth
    google_client_id = os.getenv('GOOGLE_OAUTH2_CLIENT_ID', '').strip()
    google_client_secret = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET', '').strip()
    
    if google_client_id:
        result['google']['client_id_set'] = True
        result['google']['client_id_value'] = google_client_id
        
        # Validate Client ID format
        if google_client_id.startswith(('http://', 'https://')):
            result['google']['issues'].append('Client ID has http:// or https:// prefix')
        elif not google_client_id.endswith('.apps.googleusercontent.com'):
            result['google']['issues'].append('Client ID format is incorrect (should end with .apps.googleusercontent.com)')
        elif google_client_id.count('-') < 1:
            result['google']['issues'].append('Client ID format is incorrect')
        else:
            result['google']['client_id_valid'] = True
    else:
        result['google']['issues'].append('Client ID is not set')
    
    if google_client_secret:
        result['google']['client_secret_set'] = True
    else:
        result['google']['issues'].append('Client Secret is not set')
    
    # Check GitHub OAuth
    github_client_id = os.getenv('GITHUB_CLIENT_ID', '').strip()
    github_client_secret = os.getenv('GITHUB_CLIENT_SECRET', '').strip()
    
    if github_client_id:
        result['github']['client_id_set'] = True
        result['github']['client_id_value'] = github_client_id
        result['github']['client_id_valid'] = True
    else:
        result['github']['issues'].append('Client ID is not set')
    
    if github_client_secret:
        result['github']['client_secret_set'] = True
    else:
        result['github']['issues'].append('Client Secret is not set')
    
    return result
