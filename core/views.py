from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
        # Get form data
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        # Validate passwords match
        if password1 != password2:
            messages.error(request, "Passwords don't match")
            return render(request, 'registration/signup.html')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'registration/signup.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # Log user in
            login(request, user)
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, "Error creating account")
            return render(request, 'registration/signup.html')
            
    return render(request, 'registration/signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    assignments = Assignment.objects.all()
    return render(request, 'dashboard.html', {'assignments': assignments})

@login_required
def assignment_detail(request, assignment_id):  # Updated parameter name
    assignment = get_object_or_404(Assignment, id=assignment_id)  # Updated to use id
    return render(request, 'assignment_detail.html', {'assignment': assignment})

@login_required
def my_assignments(request):
    assignments = Assignment.objects.filter(creator=request.user)
    return render(request, 'my_assignments.html', {'assignments': assignments})

@login_required
def create_assignment(request):
    if request.method == 'POST':
        # Check if description contains contact details (basic check)
        description = request.POST.get('description', '').lower()
        contact_keywords = ['email', '@', 'phone', 'contact', 'call', 'whatsapp', 'telegram']
        
        if any(keyword in description for keyword in contact_keywords):
            messages.error(request, 'Description cannot contain contact information')
            return render(request, 'create_assignment.html')
        
        # Create new assignment
        try:
            assignment = Assignment.objects.create(
                creator=request.user,
                title=request.POST['title'],
                industry=request.POST['industry'],
                duration=int(request.POST['duration']),
                rate=int(request.POST['rate']),
                requirements=request.POST['requirements'],
                description=request.POST['description']
            )
            messages.success(request, 'Assignment created successfully!')
            return redirect('my_assignments')
        except ValueError:
            messages.error(request, 'Please check the duration and rate are valid numbers')
        except Exception as e:
            messages.error(request, 'Error creating assignment. Please try again.')
    
    return render(request, 'create_assignment.html')

@login_required
def delete_assignment(request, assignment_id):
    if request.method == 'POST':
        assignment = get_object_or_404(Assignment, id=assignment_id, creator=request.user)
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully')
    return redirect('my_assignments')