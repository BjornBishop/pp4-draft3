from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, AssignmentForm
from .models import Assignment
from django.contrib import messages

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'registration/login.html')  # Updated this line

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('email')
            user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    assignments = Assignment.objects.all()
    return render(request, 'dashboard.html', {'assignments': assignments})

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    return render(request, 'assignment_detail.html', {'assignment': assignment})

@login_required
def my_assignments(request):
    assignments = Assignment.objects.filter(creator=request.user)
    return render(request, 'my_assignments.html', {'assignments': assignments})

@login_required
def create_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.creator = request.user
            assignment.save()
            return redirect('my_assignments')
    else:
        form = AssignmentForm()
    return render(request, 'create_assignment.html', {'form': form})