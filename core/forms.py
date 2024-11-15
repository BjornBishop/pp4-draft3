from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Assignment

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    phone_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'industry', 'duration', 'rate', 'requirements', 'description']