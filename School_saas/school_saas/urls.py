"""
URL configuration for school_saas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.contrib.auth.decorators import user_passes_test
from django.urls import include
from core import views  # 👈 we’ll use this for homepage

# Check function — allow only staff or superuser
def is_school_admin(user):
    return user.is_staff or user.is_superuser

# Restrict admin access
restricted_admin_view = user_passes_test(is_school_admin)(admin.site.urls)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('core/', include('core.urls')),
    path('', include('core.urls')),  # Redirect root to core app
      path('', views.home, name='home'),
]
