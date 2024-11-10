from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Assignment(models.Model):
    INDUSTRY_CHOICES = [
        ('FS', 'Financial Services'),
        ('COM', 'Commercial'),
        ('IND', 'Industrial'),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    industry = models.CharField(max_length=3, choices=INDUSTRY_CHOICES)
    duration = models.IntegerField()
    rate = models.IntegerField()
    requirements = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class MeetingRequest(models.Model):
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE)
    requester = models.ForeignKey(User, related_name='meeting_requests', on_delete=models.CASCADE)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('ACCEPTED', 'Accepted'),
            ('REJECTED', 'Rejected')
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meeting request for {self.assignment.title} by {self.requester.email}"