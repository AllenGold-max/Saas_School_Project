# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from core.models import CustomUser, School

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect to dashboard after login
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def register_school_admin(request):
    if request.method == 'POST':
        school_name = request.POST.get('school_name')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # create new school
        school = School.objects.create(name=school_name)

        # create admin user for that school
        user = CustomUser.objects.create(
            username=username,
            password=make_password(password),
            role='admin',
            school=school
        )

        messages.success(request, 'School registered successfully! You can now log in.')
        return redirect('login')

    return render(request, 'accounts/register.html')   

def logout_view(request):
    logout(request)
    return redirect('login')
