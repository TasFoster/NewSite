from django import forms
from django.contrib.auth import get_user_model

from .models import Team, TeamMembership


User = get_user_model()


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description']


class AddMemberForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    role = forms.CharField(max_length=50, required=False, label='Role')

    def __init__(self, *args, team=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.team = team

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError('No user with that username.')
        if self.team and self.team.memberships.filter(user=user).exists():
            raise forms.ValidationError('User is already a member of this team.')
        self.cleaned_data['user'] = user
        return username


class MembershipRoleForm(forms.ModelForm):
    class Meta:
        model = TeamMembership
        fields = ['role']
