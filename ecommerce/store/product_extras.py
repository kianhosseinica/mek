# store/templatetags/product_extras.py

from django import template

register = template.Library()

@register.filter
def get_variation(queryset, arg):
    """
    Expects arg in the format "size,color" (no spaces).
    Returns the first variation matching the given size and color.
    """
    try:
        size, color = arg.split(',')
        # Filter using the given size and color.
        return queryset.filter(size__name=size, color=color).first()
    except Exception:
        return None
