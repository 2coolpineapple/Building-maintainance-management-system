from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.landing_page_view, name='landing_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('maintenance/', views.dashboard, name='maintenance_dashboard'),
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('complaint/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('complaint/<int:pk>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('complaint/<int:pk>/reassign/', views.reassign_officer, name='reassign_officer'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('register/', views.registration_request_view, name='register'),
    path('track/', views.track_complaint, name='track_complaint'),
    path('help-faq/', views.help_faq_agent, name='help_faq_agent'),
    path('admin/registration_requests/', views.admin_registration_requests_view, name='admin_registration_requests'),
    path('admin/registration_requests/<int:request_id>/approve/', views.approve_registration_request_view, name='approve_registration_request'),
    path('admin/registration_requests/<int:request_id>/deny/', views.deny_registration_request_view, name='deny_registration_request'),
    path('officer/assigned_tasks/', views.assigned_tasks_view, name='assigned_tasks'),
    # Password reset URLs with custom templates in core/
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='core/custom_password_reset.html',
        email_template_name='core/custom_password_reset_email.html',
        subject_template_name='core/custom_password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/custom_password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/custom_password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/custom_password_reset_complete.html'
    ), name='password_reset_complete'),
    path('officer/dashboard/', views.officer_dashboard, name='officer_dashboard'),
    path('officer/my_complaints/', views.my_complaints, name='my_complaints'),
    path('admin/registration_requests_page/', views.registration_requests_page_view, name='registration_requests_page'),
]