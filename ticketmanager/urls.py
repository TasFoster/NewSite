from django.contrib import admin
from django.urls import path, include

from teams.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DashboardView.as_view(), name='dashboard'),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('teams/', include('teams.urls')),
    path('tickets/', include('tickets.urls')),
]
