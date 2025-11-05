from django import template

register = template.Library()

@register.filter(name='underscore_to_space')
def underscore_to_space(value):
    """Replaces underscores with spaces."""
    return value.replace('_', ' ')

@register.filter(name='HasErrors')
def has_errors(formset_errors):
    """
    Checks if a list of formset error dictionaries contains any actual errors.
    An empty dict {} signifies a valid form in the set.
    """
    if not formset_errors:
        return False
    # Check if any item in the list is a non-empty dictionary
    return any(bool(error_dict) for error_dict in formset_errors)

@register.filter(name='split')
def split(value, key):
    """
        Returns the value turned into a list.
    """
    return value.split(key)

@register.filter
def index(sequence, position):
    try:
        return sequence[position]
    except (IndexError, TypeError):
        return None

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def bold_star_labels(text):
    """Make STAR method labels (SITUATION, TASK, ACTION, RESULT) bold for better readability."""
    import re
    if not text:
        return text
    
    # Match labels at start of line or after newline, case-insensitive
    # Handles: S:, SITUATION:, T:, TASK:, A:, ACTION:, R:, RESULT:
    patterns = [
        (r'(^|\n)(\s*)(SITUATION:)', r'\1\2<strong>\3</strong>', re.MULTILINE | re.IGNORECASE),
        (r'(^|\n)(\s*)(TASK:)', r'\1\2<strong>\3</strong>', re.MULTILINE | re.IGNORECASE),
        (r'(^|\n)(\s*)(ACTION:)', r'\1\2<strong>\3</strong>', re.MULTILINE | re.IGNORECASE),
        (r'(^|\n)(\s*)(RESULT:)', r'\1\2<strong>\3</strong>', re.MULTILINE | re.IGNORECASE),
        # Single letter versions: S:, T:, A:, R:
        (r'(^|\n)(\s*)(S:)(\s)', r'\1\2<strong>\3</strong>\4', re.MULTILINE | re.IGNORECASE),
        (r'(^|\n)(\s*)(T:)(\s)', r'\1\2<strong>\3</strong>\4', re.MULTILINE | re.IGNORECASE),
        (r'(^|\n)(\s*)(A:)(\s)', r'\1\2<strong>\3</strong>\4', re.MULTILINE | re.IGNORECASE),
        (r'(^|\n)(\s*)(R:)(\s)', r'\1\2<strong>\3</strong>\4', re.MULTILINE | re.IGNORECASE),
    ]
    
    result = text
    for pattern, replacement, flags in patterns:
        result = re.sub(pattern, replacement, result)
    
    return result