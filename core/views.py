import pytz
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import SignUpForm, AssignmentForm
from .models import Assignment, MeetingRequest
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import datetime

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

@ensure_csrf_cookie
def signup_view(request):
    print("Signup view called")
    if request.method == 'POST':
        print("POST request received")
        email = request.POST.get('email')
        print(f"Checking email: {email}")
        
        # Check if email exists
        existing_user = User.objects.filter(email=email)
        print(f"Existing user query result: {existing_user.exists()}")
        
        if existing_user.exists():
            print(f"Found existing user with this email")
            messages.error(request, "Email already registered")
            return render(request, 'registration/signup.html')
        
        # If we get here, the email is not registered
        print("Email is not registered, proceeding with registration")
        
        # Get the rest of the form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        print(f"Form data: {first_name}, {last_name}, {phone_number}")
        
        # Create user
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            print(f"User created successfully: {user.email}")
            login(request, user)
            return redirect('dashboard')
            
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            messages.error(request, str(e))
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

@login_required
def request_meeting(request, assignment_id):
    if request.method == 'POST':
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Get the date and time from the form
        preferred_date = request.POST['preferred_date']
        preferred_time = request.POST['preferred_time']
        
        # Validate weekday
        date_obj = datetime.strptime(preferred_date, '%Y-%m-%d')
        if date_obj.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
            messages.error(request, 'Weekend dates are not available for meetings.')
            return redirect('assignment_detail', assignment_id=assignment_id)
        
        # Validate time slot
        time_obj = datetime.strptime(preferred_time, '%H:%M').time()
        morning_start = datetime.strptime('10:00', '%H:%M').time()
        morning_end = datetime.strptime('11:30', '%H:%M').time()
        afternoon_start = datetime.strptime('13:00', '%H:%M').time()
        afternoon_end = datetime.strptime('17:00', '%H:%M').time()
        
        if not ((morning_start <= time_obj <= morning_end) or 
                (afternoon_start <= time_obj <= afternoon_end)):
            messages.error(request, 'Please select a valid time slot.')
            return redirect('assignment_detail', assignment_id=assignment_id)
        
        # Create meeting request
        meeting_request = MeetingRequest.objects.create(
            assignment=assignment,
            requester=request.user,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            timezone='Europe/London',
            message=request.POST.get('message', '')
        )
        
        # Send email notifications with timezone information
        subject = f'New Meeting Request for {assignment.title}'
        message = f'''
        You have a new meeting request from {request.user.get_full_name()}
        Assignment: {assignment.title}
        Preferred Date: {meeting_request.preferred_date}
        Preferred Time: {meeting_request.preferred_time} (UTC+1 London)
        Message: {meeting_request.message}
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [assignment.creator.email],
            fail_silently=True,
        )
        
        messages.success(request, 'Meeting request sent successfully!')
        return redirect('assignment_detail', assignment_id=assignment_id)
        
    return redirect('assignment_detail', assignment_id=assignment_id)