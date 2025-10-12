from django.http import HttpResponse
from django.shortcuts import redirect

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            user_role = request.user.role
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("Access Denied: You don't have permission to view this page.")
        return wrapper_func
    return decorator
