from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    return render(request, 'core/dashboard.html', context)

def home(request):
    return render(request, 'core/home.html')

@login_required
def students(request):
    return render(request, 'core/students.html')  # make this template next

@login_required
def classes(request):
    return render(request, 'core/classes.html')

@login_required
def teachers_view(request):
    return render(request, 'core/teachers.html')
