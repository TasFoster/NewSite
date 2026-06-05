from django import forms

from .models import Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'assignee', 'status']

    def __init__(self, *args, team=None, user=None, is_captain=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.team = team
        if team is not None:
            self.fields['assignee'].queryset = team.members.all()
            self.fields['assignee'].required = False
        if not is_captain:
            # Members can't reassign tickets to others on create — lock to themselves or none.
            self.fields['assignee'].disabled = True
            if user is not None and self.instance.pk is None:
                self.fields['assignee'].initial = user
