from django import template

register = template.Library()

@register.filter
def addclass(field, css_class):
    """Add a CSS class to a form field."""
    return field.as_widget(attrs={"class": css_class})

@register.filter
def filter_status(complaints, status):
    """Filter complaints by status."""
    return [c for c in complaints if c.status == status]