from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ComplaintCategory, Complaint, StatusLog, Feedback, RegistrationRequest

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_officer', 'department')
    list_filter = ('is_staff', 'is_officer', 'department')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Officer Details', {'fields': ('is_officer', 'department', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_officer', 'department'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'department')

@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'location', 'user', 'assigned_officer', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('location', 'description', 'user__username', 'assigned_officer__username')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'assigned_officer')
    actions = ['mark_in_progress', 'mark_resolved']

    def mark_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
    mark_in_progress.short_description = 'Mark selected complaints as in progress'

    def mark_resolved(self, request, queryset):
        queryset.update(status='resolved')
    mark_resolved.short_description = 'Mark selected complaints as resolved'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.is_officer:
            return qs.filter(assigned_officer=request.user)
        return qs.filter(user=request.user)

@admin.register(StatusLog)
class StatusLogAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'status', 'created_at', 'updated_by')
    list_filter = ('status', 'created_at')
    search_fields = ('complaint__id', 'remarks')
    raw_id_fields = ('complaint', 'updated_by')
    readonly_fields = ('created_at',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('complaint__id', 'comments')
    raw_id_fields = ('complaint',)
    readonly_fields = ('created_at',)

@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'department', 'role', 'status')
    list_filter = ('status', 'department', 'role')
    search_fields = ('full_name', 'email', 'phone', 'department', 'role')
    actions = ['approve_requests', 'deny_requests']

    def approve_requests(self, request, queryset):
        queryset.update(status='approved')
    approve_requests.short_description = 'Approve selected registration requests'

    def deny_requests(self, request, queryset):
        queryset.update(status='denied')
    deny_requests.short_description = 'Deny selected registration requests'