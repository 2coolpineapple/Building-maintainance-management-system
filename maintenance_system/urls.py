from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('/maintenance/'), name='home'),
    path('admin/', admin.site.urls),
    path('maintenance/', include('core.urls')),
    path('accounts/', include('core.urls')),
]
