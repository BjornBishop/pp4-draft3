from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Assignment, MeetingRequest

# Register your models here.

# Customize the Admin Site
admin.site.site_header = 'SagaCity Administration'
admin.site.site_title = 'SagaCity Admin Portal'
admin.site.index_title = 'Welcome to SagaCity Admin Portal'

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

# Unregister and register a custom user admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'industry', 'duration', 'rate', 'created_at')
    list_filter = ('industry', 'created_at')
    search_fields = ('title', 'description', 'requirements')
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'creator', 'industry')
        }),
        ('Details', {
            'fields': ('duration', 'rate', 'requirements', 'description')
        }),
    )

@admin.register(MeetingRequest)
class MeetingRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'assignment', 'preferred_date', 'preferred_time', 'status', 'created_at')
    list_filter = ('status', 'preferred_date')
    search_fields = ('requester__email', 'assignment__title')
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    fieldsets = (
        ('Request Information', {
            'fields': ('requester', 'assignment', 'status')
        }),
        ('Meeting Details', {
            'fields': ('preferred_date', 'preferred_time', 'message')
        }),
    )
    
    actions = ['accept_meetings', 'reject_meetings']
    
    def accept_meetings(self, request, queryset):
        updated = queryset.update(status='ACCEPTED')
        self.message_user(request, f'{updated} meeting(s) have been accepted.')
        
        # Send email notifications for acceptance
        for meeting in queryset:
            send_mail(
                'Meeting Request Accepted',
                f'Your meeting request for {meeting.assignment.title} on {meeting.preferred_date} at {meeting.preferred_time} has been accepted.',
                'from@example.com',
                [meeting.requester.email],
                fail_silently=True,
            )
    accept_meetings.short_description = "Accept selected meeting requests"
    
    def reject_meetings(self, request, queryset):
        updated = queryset.update(status='REJECTED')
        self.message_user(request, f'{updated} meeting(s) have been rejected.')
        
        # Send email notifications for rejection
        for meeting in queryset:
            send_mail(
                'Meeting Request Update',
                f'Unfortunately, your meeting request for {meeting.assignment.title} on {meeting.preferred_date} at {meeting.preferred_time} could not be accommodated.',
                'from@example.com',
                [meeting.requester.email],
                fail_silently=True,
            )
    reject_meetings.short_description = "Reject selected meeting requests"
    
    def has_add_permission(self, request):
        return False  # Stops the admin from making meeting requests with self 