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
