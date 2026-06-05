from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from .models import Team


def is_captain(user, team):
    return user.is_authenticated and team.captain_id == user.id


def is_member(user, team):
    if not user.is_authenticated:
        return False
    return team.memberships.filter(user=user).exists()


class TeamAccessMixin(LoginRequiredMixin):
    """Resolve self.team from URL kwarg `team_id` and require member access."""

    captain_only = False

    def dispatch(self, request, *args, **kwargs):
        self.team = get_object_or_404(Team, pk=kwargs['team_id'])
        if not is_member(request.user, self.team):
            raise PermissionDenied('You are not a member of this team.')
        if self.captain_only and not is_captain(request.user, self.team):
            raise PermissionDenied('Only the team captain can perform this action.')
        return super().dispatch(request, *args, **kwargs)
