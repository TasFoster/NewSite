from django.urls import path

from . import views

urlpatterns = [
    path('team/<int:team_id>/new/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('<int:pk>/edit/', views.TicketEditView.as_view(), name='ticket_edit'),
    path('<int:pk>/status/', views.TicketStatusView.as_view(), name='ticket_status'),
    path('<int:pk>/delete/', views.TicketDeleteView.as_view(), name='ticket_delete'),
]
