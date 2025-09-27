from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    is_officer = models.BooleanField(default=False)
    # Remove is_staff field to use AbstractUser's is_staff field
    # is_staff = models.BooleanField(default=False)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        # Ensure superusers are not marked as staff
        if self.is_superuser:
            self.is_staff = False
        super().save(*args, **kwargs)

class ComplaintCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved')
    ]

    ZONE_CHOICES = [
        ('northern', 'Northern'),
        ('southern', 'Southern'),
        ('eastern', 'Eastern'),
        ('western', 'Western'),
        ('central', 'Central'),
    ]

    BUILDING_CHOICES = [
        ('main_station', 'Main Station'),
        ('platform', 'Platform'),
        ('office', 'Office'),
        ('other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    NATURE_OF_ISSUE_CHOICES = [
        ('non_functional', 'Non-Functional'),
        ('damaged', 'Damaged'),
        ('other', 'Other'),
    ]

    category = models.ForeignKey(ComplaintCategory, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints', null=True, blank=True)
    assigned_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_complaints')
    location = models.CharField(max_length=200)
    preferred_resolution_department = models.CharField(max_length=100, blank=True)
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES, blank=True)
    station = models.CharField(max_length=100, blank=True)
    building = models.CharField(max_length=20, choices=BUILDING_CHOICES, blank=True)
    floor_room = models.CharField(max_length=100, blank=True)
    equipment_id = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    contact_number = models.CharField(max_length=20, blank=True)
    nature_of_issue = models.CharField(max_length=20, choices=NATURE_OF_ISSUE_CHOICES, blank=True)
    media_upload = models.FileField(upload_to='complaint_media/', blank=True, null=True)
    acknowledgment = models.BooleanField(default=False)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolution_remarks = models.TextField(blank=True)

    def __str__(self):
        return f'{self.category} - {self.location} ({self.status})'

class StatusLog(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='status_logs')
    status = models.CharField(max_length=20)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent')
    ]

    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class RegistrationRequest(models.Model):
    ROLE_CHOICES = [
        ('officer', 'Officer'),
        ('maintenance', 'Maintenance Staff'),
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('denied', 'Denied')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.role}) - {self.status}"

    address = models.TextField(blank=True)
    qualifications = models.TextField(blank=True)
    experience = models.CharField(max_length=100, blank=True)