# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

@role_required(['admin', 'teacher'])
def dashboard(request):
    user = request.user
    context = {'user': user}
    return render(request, 'core/dashboard.html', context)
