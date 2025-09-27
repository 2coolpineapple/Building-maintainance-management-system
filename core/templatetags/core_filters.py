from django import template

register = template.Library()

@register.filter(name='filter_status')
def filter_status(complaints, status):
    """Filter complaints by their status.
    Status values must match Complaint.STATUS_CHOICES: 'pending', 'in_progress', 'resolved'
    """
    if not complaints:
        return []
    return [complaint for complaint in complaints if complaint.status == status]