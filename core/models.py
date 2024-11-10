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