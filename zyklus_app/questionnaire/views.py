
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy

from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

import questionnaire.models
from .models import PseudoUser


# Create your views here.
@login_required(login_url='/')
def test(request):
    context = {'page_title': 'Test'}
    return render(request, 'questionnaire/test.html', context)


# creates a new Pair
class CreatePairView(StaffuserRequiredMixin, LoginRequiredMixin, CreateView):
    model = questionnaire.models.Pair
    fields = ['ident']
    template_name = 'questionnaire/pair_form.html'
    success_url = 'pair_list'
    login_url = 'member:login'


# shows a list of Pairs
class PairListView(StaffuserRequiredMixin, LoginRequiredMixin, ListView):
    model = questionnaire.models.Pair
    ordering = 'ident'


# changes a Pair
class PairUpdateView(UpdateView):
    model = questionnaire.models.Pair
    fields = ['ident']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse_lazy('questionnaire:pair_list')


# confirm the deletion of a Pair
class PairDeleteView(StaffuserRequiredMixin, LoginRequiredMixin, DeleteView):
    model = questionnaire.models.Pair
    success_url = reverse_lazy('questionnaire:pair_list')


# shows a selected Pair
class PairDetailView(StaffuserRequiredMixin, LoginRequiredMixin, DetailView):
    model = questionnaire.models.Pair

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
