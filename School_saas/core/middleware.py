from django.shortcuts import redirect

class RestrictAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and not request.user.is_superuser:
            return redirect('/')  # redirect non-admins to homepage
        return self.get_response(request)
