from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, TemplateView, View

from tickets.models import Ticket

from .forms import AddMemberForm, MembershipRoleForm, TeamForm
from .models import Team, TeamMembership
from .permissions import TeamAccessMixin


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'teams/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['captained_teams'] = user.captained_teams.all()
        ctx['member_teams'] = user.teams.exclude(captain=user)
        return ctx


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = 'teams/team_form.html'

    def form_valid(self, form):
        form.instance.captain = self.request.user
        response = super().form_valid(form)
        TeamMembership.objects.create(
            team=self.object,
            user=self.request.user,
            role='Captain',
        )
        return response

    def get_success_url(self):
        return reverse('team_detail', args=[self.object.id])


class TeamDetailView(TeamAccessMixin, TemplateView):
    template_name = 'teams/team_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tickets = self.team.tickets.select_related('assignee', 'created_by')
        columns = []
        for value, label in Ticket.Status.choices:
            columns.append({
                'key': value,
                'label': label,
                'tickets': [t for t in tickets if t.status == value],
            })
        ctx['team'] = self.team
        ctx['columns'] = columns
        ctx['memberships'] = self.team.memberships.select_related('user')
        ctx['is_captain'] = self.request.user.id == self.team.captain_id
        return ctx


class MembersView(TeamAccessMixin, TemplateView):
    template_name = 'teams/members.html'
    captain_only = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['team'] = self.team
        ctx['memberships'] = self.team.memberships.select_related('user')
        ctx['add_form'] = AddMemberForm(team=self.team)
        return ctx


class AddMemberView(TeamAccessMixin, View):
    captain_only = True

    def post(self, request, team_id):
        form = AddMemberForm(request.POST, team=self.team)
        if form.is_valid():
            TeamMembership.objects.create(
                team=self.team,
                user=form.cleaned_data['user'],
                role=form.cleaned_data.get('role', ''),
            )
            return redirect('team_members', team_id=self.team.id)
        memberships = self.team.memberships.select_related('user')
        return render(request, 'teams/members.html', {
            'team': self.team,
            'memberships': memberships,
            'add_form': form,
        })


class EditMembershipView(TeamAccessMixin, View):
    captain_only = True

    def get_membership(self, pk):
        return get_object_or_404(TeamMembership, pk=pk, team=self.team)

    def get(self, request, team_id, pk):
        membership = self.get_membership(pk)
        form = MembershipRoleForm(instance=membership)
        return render(request, 'teams/membership_edit.html', {
            'team': self.team,
            'membership': membership,
            'form': form,
        })

    def post(self, request, team_id, pk):
        membership = self.get_membership(pk)
        form = MembershipRoleForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            return redirect('team_members', team_id=self.team.id)
        return render(request, 'teams/membership_edit.html', {
            'team': self.team,
            'membership': membership,
            'form': form,
        })


class RemoveMembershipView(TeamAccessMixin, View):
    captain_only = True

    def post(self, request, team_id, pk):
        membership = get_object_or_404(TeamMembership, pk=pk, team=self.team)
        if membership.user_id == self.team.captain_id:
            # Don't allow removing the captain via this view
            return redirect('team_members', team_id=self.team.id)
        membership.delete()
        return redirect('team_members', team_id=self.team.id)
