from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q, Subquery, OuterRef
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ComplaintForm, ComplaintUpdateForm, FeedbackForm, OfficerAssignmentForm, RegistrationRequestForm
from .models import Complaint, User, StatusLog, Feedback, ComplaintCategory, RegistrationRequest

from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.hashers import make_password
import random
import string

from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Officer assigned tasks view
@login_required
def assigned_tasks_view(request):
    if not request.user.is_officer:
        return redirect('login')
    # Only show complaints where the latest status log is 'assigned_to_staff' and updated_by this officer
    latest_logs = StatusLog.objects.filter(
        complaint=OuterRef('pk')
    ).order_by('-created_at')
    assigned_tasks = Complaint.objects.filter(
        assigned_officer__is_staff=True,
        status_logs__status='assigned_to_staff',
        status_logs__updated_by=request.user,
        status_logs__created_at=Subquery(latest_logs.values('created_at')[:1])
    ).distinct().order_by('-created_at')
    return render(request, 'core/assigned_tasks.html', {'assigned_tasks': assigned_tasks})

def registration_request_view(request):
    if request.method == 'POST':
        form = RegistrationRequestForm(request.POST)
        if form.is_valid():
            # For all roles including maintenance, save registration request for admin approval
            form.save()
            messages.success(request, 'Registration request submitted successfully. Please wait for admin approval.')
            return redirect('/maintenance/login/')
    else:
        form = RegistrationRequestForm()
    return render(request, 'core/registration.html', {'form': form})

def admin_registration_requests_view(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Unauthorized access.')
        return redirect('login')
    pending_requests = RegistrationRequest.objects.filter(status='pending')
    accepted_requests = RegistrationRequest.objects.filter(status='accepted')
    denied_requests = RegistrationRequest.objects.filter(status='denied')
    context = {
        'pending_requests': pending_requests,
        'accepted_requests': accepted_requests,
        'denied_requests': denied_requests,
    }
    return render(request, 'core/admin_registration_requests.html', context)

def approve_registration_request_view(request, request_id):
    if not request.user.is_staff:
        messages.error(request, 'Unauthorized access.')
        return redirect('login')
    reg_request = get_object_or_404(RegistrationRequest, id=request_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            # Generate username and password
            prefix_map = {
                'admin': 'admin',
                'officer': 'officer',
                'maintenance': 'staff',
                'user': 'user',
            }
            prefix = prefix_map.get(reg_request.role, 'user')

            # Generate short random alphanumeric string of length 3
            random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=3))

            # Extract one word from department (e.g., first word)
            department_words = reg_request.department.split() if reg_request.department else []
            department_part = department_words[0].lower() if department_words else ''

            username = f"{prefix}{random_str}{department_part}"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            # Create user
            user = User.objects.create(
                username=username,
                email=reg_request.email,
                is_officer=(reg_request.role == 'officer'),
                is_staff=(reg_request.role == 'maintenance'),
                department=reg_request.department,
                phone=reg_request.phone,
                password=make_password(password),
            )
            user.save()
            reg_request.status = 'accepted'
            reg_request.save()

            # Send email with username and password to the new user
            subject = 'Your account has been approved'
            message = f'Hello {reg_request.full_name},\n\nYour registration request has been approved.\n\nUsername: {username}\nPassword: {password}\n\nPlease log in and change your password immediately.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [reg_request.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=True)

            messages.success(request, f'Registration request accepted. Username: {username}, Password: {password}')
        elif action == 'deny':
            reg_request.status = 'denied'
            reg_request.save()
            messages.success(request, 'Registration request denied.')
        return redirect('admin_registration_requests')
    return render(request, 'core/approve_registration_request.html', {'request_obj': reg_request})

def deny_registration_request_view(request, request_id):
    if not request.user.is_staff:
        messages.error(request, 'Unauthorized access.')
        return redirect('login')
    reg_request = get_object_or_404(RegistrationRequest, id=request_id)
    if request.method == 'POST':
        reg_request.status = 'denied'
        reg_request.save()
        messages.success(request, 'Registration request denied.')
        return redirect('admin_registration_requests')
    return render(request, 'core/approve_registration_request.html', {'request_obj': reg_request})

from django.shortcuts import redirect

@login_required
def dashboard(request):
    if request.user.is_superuser:
        complaints = Complaint.objects.all()
        categories = ComplaintCategory.objects.all()
        officers = User.objects.filter(is_officer=True)
        registration_requests = RegistrationRequest.objects.filter(status='pending')
        context = {
            'complaints': complaints,
            'categories': categories,
            'officers': officers,
            'registration_requests': registration_requests,
        }
        return render(request, 'core/dashboard.html', context)
    elif request.user.is_officer:
        return redirect('officer_dashboard')
    elif request.user.is_staff:
        complaints = Complaint.objects.filter(assigned_officer=request.user)
        total_complaints = complaints.count()
        pending_complaints = complaints.filter(status='pending').count()
        in_progress_complaints = complaints.filter(status='in_progress').count()
        resolved_complaints = complaints.filter(status='resolved').count()

        context = {
            'complaints': complaints,
            'total_complaints': total_complaints,
            'pending_complaints': pending_complaints,
            'in_progress_complaints': in_progress_complaints,
            'resolved_complaints': resolved_complaints,
        }
        return render(request, 'core/staff_dashboard.html', context)
    else:
        complaints = Complaint.objects.filter(user=request.user)
        return render(request, 'core/dashboard.html', {'complaints': complaints})

def officer_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_officer:
        return redirect('login')
        
    complaints = Complaint.objects.filter(assigned_officer=request.user)
    total_complaints = complaints.count()
    pending_complaints = complaints.filter(status='pending').count()
    in_progress_complaints = complaints.filter(status='in_progress').count()
    resolved_complaints = complaints.filter(status='resolved').count()
    
    context = {
        'complaints': complaints,
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'in_progress_complaints': in_progress_complaints,
        'resolved_complaints': resolved_complaints
    }
    
    return render(request, 'core/officer_dashboard.html', context)

@login_required
def my_complaints(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Show only complaints submitted by the user, regardless of staff/officer
    complaints = Complaint.objects.filter(user=request.user)

    context = {
        'complaints': complaints,
    }
    return render(request, 'core/my_complaints.html', context)

def submit_complaint(request):
    # Mapping from complaint category names to officer departments (all lowercase keys and values)
    category_to_department = {
        'electrical': 'electrical',
        'plumbing': 'plumbing',
        'cleaning': 'cleaning',
        'security': 'security',
        'it': 'it',
        'telecom': 'telecom',
        # Add other mappings as needed
    }

    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            if request.user.is_authenticated:
                complaint.user = request.user
            
            category_name = complaint.category.name.lower()
            department_name = category_to_department.get(category_name, None)
            
            available_officer = None
            if category_name:
                first_word = category_name.split()[0]
                available_officer = User.objects.filter(
                    is_officer=True,
                    username__icontains=first_word
                ).first()

            if not available_officer:
                # Assign to admin (superuser)
                available_officer = User.objects.filter(is_superuser=True).first()

            complaint.assigned_officer = available_officer
            complaint.save()
            
            # Create initial status log
            StatusLog.objects.create(
                complaint=complaint,
                status='pending',
                updated_by=request.user if request.user.is_authenticated else None
            )
            
            # Send email notification
            if available_officer:
                send_mail(
                    'New Complaint Assigned',
                    f'A new complaint has been assigned to you: {complaint.category} - {complaint.location}',
                    settings.DEFAULT_FROM_EMAIL,
                    [available_officer.email],
                    fail_silently=True,
                )
            
            messages.success(request, 'Complaint submitted successfully! Your complaint ID is: ' + str(complaint.pk))
            return redirect('complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintForm()
    
    return render(request, 'core/submit_complaint.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') == 'on'

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)  # Session expires on browser close
            # Clear messages after redirect to avoid duplicate display
            if user.is_superuser:
                response = redirect('/accounts/admin/dashboard/')
            else:
                response = redirect('dashboard')
            list(messages.get_messages(request))  # Clear messages
            return response
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')

def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    status_logs = StatusLog.objects.filter(complaint=complaint).order_by('-created_at')
    feedback = None
    if request.user == complaint.user:
        feedback = Feedback.objects.filter(complaint=complaint).first()

    if request.method == 'POST' and (request.user.is_staff or request.user == complaint.assigned_officer):
        form = ComplaintUpdateForm(request.POST)
        if form.is_valid():
            complaint.status = form.cleaned_data['status']
            complaint.resolution_remarks = form.cleaned_data['resolution_remarks']
            complaint.save()

            StatusLog.objects.create(
                complaint=complaint,
                status=complaint.status,
                remarks=complaint.resolution_remarks,
                updated_by=request.user
            )
            messages.success(request, 'Complaint status updated successfully.')
            return redirect('complaint_detail', pk=pk)
    else:
        form = ComplaintUpdateForm(initial={
            'status': complaint.status,
            'resolution_remarks': complaint.resolution_remarks
        })

    context = {
        'complaint': complaint,
        'status_logs': status_logs,
        'feedback': feedback,
        'form': form,
    }
    return render(request, 'core/complaint_detail.html', context)

def submit_feedback(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.complaint = complaint
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Feedback submitted successfully.')
            return redirect('complaint_detail', pk=pk)
    else:
        form = FeedbackForm()

    return render(request, 'core/submit_feedback.html', {'form': form, 'complaint': complaint})

from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):

    complaints = Complaint.objects.all()
    categories = ComplaintCategory.objects.all()
    officers = User.objects.filter(is_officer=True)
    staff_members = User.objects.filter(is_staff=True, is_officer=False)
    registration_requests = RegistrationRequest.objects.filter(status='pending')

    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        new_officer_id = request.POST.get('new_officer')
        complaint = get_object_or_404(Complaint, pk=complaint_id)
        new_officer = get_object_or_404(User, pk=new_officer_id, is_officer=True)
        complaint.assigned_officer = new_officer
        complaint.save()
        messages.success(request, 'Officer reassigned successfully.')
        return redirect('admin_dashboard')

    form = OfficerAssignmentForm()
    return render(request, 'core/admin_dashboard.html', {
        'complaints': complaints,
        'categories': categories,
        'officers': officers,
        'staff_members': staff_members,
        'form': form,
        'registration_requests': registration_requests,
    })

def reassign_officer(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)

    # Corrected assignment type based on user role
    if request.user.is_staff:
        assignment_type = 'officer'
        category_first_word = None
    else:
        assignment_type = 'staff'
        # Only show staff whose username contains the first word of the category
        category_first_word = complaint.category.name.split()[0].lower() if complaint.category and complaint.category.name else None

    if request.method == 'POST':
        form = OfficerAssignmentForm(request.POST, assignment_type=assignment_type, category_first_word=category_first_word)
        if form.is_valid():
            new_user = form.cleaned_data['assigned_user']
            complaint.assigned_officer = new_user
            complaint.save()
            # Log the assignment if officer is assigning to staff
            if assignment_type == 'staff':
                StatusLog.objects.create(
                    complaint=complaint,
                    status='assigned_to_staff',
                    remarks='Assigned to staff by officer',
                    updated_by=request.user
                )
            messages.success(request, f'{assignment_type.capitalize()} reassigned successfully.')
            return redirect('complaint_detail', pk=pk)
    else:
        initial_user = complaint.assigned_officer if assignment_type == 'officer' else getattr(complaint, 'assigned_staff', None)
        form = OfficerAssignmentForm(initial={'assigned_user': initial_user}, assignment_type=assignment_type, category_first_word=category_first_word)

    return render(request, 'core/reassign_officer.html', {'form': form, 'complaint': complaint, 'assignment_type': assignment_type})

from .models import ComplaintCategory
from django.http import HttpResponseRedirect
from django.urls import reverse

def landing_page_view(request):
    popular_categories = ComplaintCategory.objects.all()[:5]  # Get top 5 categories
    contact_info = {
        'phone': '+91 12345 67890',
        'email': 'support@indianrailways.gov.in',
        'emergency': '100',
    }
    context = {
        'popular_categories': popular_categories,
        'contact_info': contact_info,
    }
    return render(request, 'core/landing.html', context)

from .models import Complaint

def track_complaint(request):
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        if complaint_id and complaint_id.isdigit():
            try:
                complaint = Complaint.objects.get(pk=int(complaint_id))
                return HttpResponseRedirect(reverse('complaint_detail', kwargs={'pk': int(complaint_id)}))
            except Complaint.DoesNotExist:
                return render(request, 'core/track_complaint.html', {'error': 'Complaint ID not found. Please enter a valid complaint ID.'})
        else:
            # Invalid input, reload the form with an error message
            return render(request, 'core/track_complaint.html', {'error': 'Please enter a valid complaint ID.'})
    return render(request, 'core/track_complaint.html')

import os
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_staff)
def registration_requests_page_view(request):
    pending_requests = RegistrationRequest.objects.filter(status='pending')
    accepted_requests = RegistrationRequest.objects.filter(status='accepted')
    denied_requests = RegistrationRequest.objects.filter(status='denied')
    context = {
        'pending_requests': pending_requests,
        'accepted_requests': accepted_requests,
        'denied_requests': denied_requests,
    }
    return render(request, 'core/registration_request.html', context)

def help_faq_agent(request):
    return render(request, 'core/help_faq_agent.html')
