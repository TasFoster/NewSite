from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import View

from teams.models import Team
from teams.permissions import TeamAccessMixin, is_captain, is_member

from .forms import TicketForm
from .models import Ticket


class TicketCreateView(TeamAccessMixin, View):
    def get(self, request, team_id):
        form = TicketForm(
            team=self.team,
            user=request.user,
            is_captain=is_captain(request.user, self.team),
        )
        return render(request, 'tickets/ticket_form.html', {
            'team': self.team,
            'form': form,
        })

    def post(self, request, team_id):
        form = TicketForm(
            request.POST,
            team=self.team,
            user=request.user,
            is_captain=is_captain(request.user, self.team),
        )
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.team = self.team
            ticket.created_by = request.user
            if not is_captain(request.user, self.team):
                ticket.assignee = request.user
            ticket.set_status(ticket.status)
            ticket.save()
            return redirect('ticket_detail', pk=ticket.id)
        return render(request, 'tickets/ticket_form.html', {
            'team': self.team,
            'form': form,
        })


class _TicketBaseView(LoginRequiredMixin, View):
    def get_ticket(self, pk):
        ticket = get_object_or_404(Ticket.objects.select_related('team', 'assignee', 'created_by'), pk=pk)
        if not is_member(self.request.user, ticket.team):
            raise PermissionDenied('You are not a member of this team.')
        return ticket


class TicketDetailView(_TicketBaseView):
    def get(self, request, pk):
        ticket = self.get_ticket(pk)
        captain = is_captain(request.user, ticket.team)
        can_change_status = captain or ticket.assignee_id == request.user.id or ticket.created_by_id == request.user.id
        return render(request, 'tickets/ticket_detail.html', {
            'ticket': ticket,
            'team': ticket.team,
            'is_captain': captain,
            'can_change_status': can_change_status,
            'status_choices': Ticket.Status.choices,
        })


class TicketEditView(_TicketBaseView):
    def get(self, request, pk):
        ticket = self.get_ticket(pk)
        if not (is_captain(request.user, ticket.team) or ticket.created_by_id == request.user.id):
            raise PermissionDenied('Only the captain or the ticket author can edit this ticket.')
        form = TicketForm(
            instance=ticket,
            team=ticket.team,
            user=request.user,
            is_captain=is_captain(request.user, ticket.team),
        )
        return render(request, 'tickets/ticket_form.html', {
            'team': ticket.team,
            'form': form,
            'ticket': ticket,
        })

    def post(self, request, pk):
        ticket = self.get_ticket(pk)
        if not (is_captain(request.user, ticket.team) or ticket.created_by_id == request.user.id):
            raise PermissionDenied('Only the captain or the ticket author can edit this ticket.')
        form = TicketForm(
            request.POST,
            instance=ticket,
            team=ticket.team,
            user=request.user,
            is_captain=is_captain(request.user, ticket.team),
        )
        if form.is_valid():
            t = form.save(commit=False)
            t.set_status(t.status)
            t.save()
            return redirect('ticket_detail', pk=t.id)
        return render(request, 'tickets/ticket_form.html', {
            'team': ticket.team,
            'form': form,
            'ticket': ticket,
        })


class TicketStatusView(_TicketBaseView):
    def post(self, request, pk):
        ticket = self.get_ticket(pk)
        new_status = request.POST.get('status')
        if new_status not in dict(Ticket.Status.choices):
            raise PermissionDenied('Invalid status.')
        captain = is_captain(request.user, ticket.team)
        is_owner = ticket.assignee_id == request.user.id or ticket.created_by_id == request.user.id
        if not (captain or is_owner):
            raise PermissionDenied('You cannot change the status of this ticket.')
        ticket.set_status(new_status)
        ticket.save(update_fields=['status', 'completed_at', 'updated_at'])
        return redirect('ticket_detail', pk=ticket.id)


class TicketDeleteView(_TicketBaseView):
    def post(self, request, pk):
        ticket = self.get_ticket(pk)
        if not is_captain(request.user, ticket.team):
            raise PermissionDenied('Only the captain can delete tickets.')
        team_id = ticket.team_id
        ticket.delete()
        return redirect('team_detail', team_id=team_id)
