"""
Utility functions for security and validation.
"""
from django.core.exceptions import ValidationError
from django.conf import settings
import bleach

def validate_file_size(file, max_size, field_name="File"):
    """
    Validate file size.
    
    Args:
        file: Uploaded file object
        max_size: Maximum file size in bytes
        field_name: Name of the field for error message
    
    Raises:
        ValidationError: If file size exceeds limit
    """
    if file.size > max_size:
        size_mb = max_size / (1024 * 1024)
        raise ValidationError(f"{field_name} size exceeds {size_mb:.1f}MB limit.")


def sanitize_html(text):
    """
    Sanitize HTML input to prevent XSS attacks.
    
    Args:
        text: HTML text to sanitize
    
    Returns:
        str: Sanitized HTML text
    """
    if not text:
        return text
    
    # Allowed HTML tags
    allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'b', 'i', 'u']
    
    # Sanitize HTML
    sanitized = bleach.clean(text, tags=allowed_tags, strip=True)
    
    return sanitized


def sanitize_text(text):
    """
    Escape HTML characters in plain text.
    
    Args:
        text: Text to escape
    
    Returns:
        str: Escaped text
    """
    if not text:
        return text
    
    from django.utils.html import escape
    return escape(text)

