from django import template

register = template.Library()

@register.filter
def sum_refunded(queryset):
    """Returns the total refunded quantity for an order item."""
    if queryset:
        return sum(refund.quantity for refund in queryset)
    return 0  # If no refunds exist, return 0

@register.filter
def subtract(value, arg):
    """Subtracts two values."""
    return value - arg if value and arg else value  # Ensure no subtraction errors
