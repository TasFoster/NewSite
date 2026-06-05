from django.urls import path

from . import views

urlpatterns = [
    path('new/', views.TeamCreateView.as_view(), name='team_create'),
    path('<int:team_id>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('<int:team_id>/members/', views.MembersView.as_view(), name='team_members'),
    path('<int:team_id>/members/add/', views.AddMemberView.as_view(), name='team_member_add'),
    path('<int:team_id>/members/<int:pk>/edit/', views.EditMembershipView.as_view(), name='team_member_edit'),
    path('<int:team_id>/members/<int:pk>/remove/', views.RemoveMembershipView.as_view(), name='team_member_remove'),
]
