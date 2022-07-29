import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages

import questionnaire
from service.services import Service
from .models import PseudoUser, QuestionnaireDaily, QuestionnaireStart, QuestionnaireEnd
from .forms import QuestionnaireStartForm


# Create your views here.
# logical process
@login_required(login_url='/')
def landing_page(request):
    # fetches the user from the database
    pseudo_user = get_object_or_404(PseudoUser, pk=request.user.pk)
    daily_questionnaires = QuestionnaireDaily.objects.filter(
        pseudo_user__exact=request.user)  # fetches all DailyQuestionnaires of this user

    # fetches questionnaire_/ -start and -end
    questionnaire_start = QuestionnaireStart.objects.filter(pseudo_user__exact=request.user)
    if questionnaire_start.count() == 0:
        questionnaire_start = None
    questionnaire_end = QuestionnaireEnd.objects.filter(pseudo_user__exact=request.user)
    if questionnaire_end.count() == 0:
        questionnaire_end = None

    # render admin interface if Staff or Superuser
    if request.user.is_superuser or request.user.is_staff:
        context = {'page_title': 'Admin-interface'}
        return render(request, 'questionnaire/admin_interface.html', context)
    else:
        # Program flow for normal users
        # render create_sq if the Users questionnaire_start is None
        if questionnaire_start is None:
            return redirect('questionnaire:create_sq')

        if daily_questionnaires.count() < Service.PERIOD:
            # tests whether a dq has already been created today
            if not daily_questionnaires.filter(date__contains=datetime.date.today(),
                                               date__startswith=datetime.date.today()):
                return redirect('questionnaire:create_dq')
            else:
                context = {'page_title': 'Vielen Dank!', 'pseudo_user': pseudo_user}
                return render(request, 'questionnaire/dq_already.html', context)

        if questionnaire_end is None:
            return redirect('questionnaire:create_eq')

        # Todo render success page
        context = {'page_title': 'Vielen Dank!', 'pseudo_user': pseudo_user}
        return render(request, 'questionnaire/success.html', context)


# downloads the data of a pair
@staff_member_required(login_url='questionnaire:landing_page')
def download_pair_data(request, pk):
    return Service.download_data_service(pk)


# downloads the data of a pair excluding start- an end-questionnaire
@staff_member_required(login_url='questionnaire:landing_page')
def download_all_data(request):
    return Service.download_data_service(None)


# creates a new Pair
class CreatePairView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = questionnaire.models.Pair
    fields = ['ident']
    template_name = 'questionnaire/pair_form.html'
    success_url = 'pair_list'
    login_url = 'member:login'

    def test_func(self):
        return self.request.user.is_staff


# shows a list of Pairs
class PairListView(UserPassesTestMixin, LoginRequiredMixin, ListView):
    model = questionnaire.models.Pair
    ordering = 'ident'

    def get_context_data(self, **kwargs):
        pseudo_users = PseudoUser.objects.all()

        context = super().get_context_data(**kwargs)
        context['pseudo_user'] = pseudo_users
        return context

    def test_func(self):
        return self.request.user.is_staff


# changes a Pair
class PairUpdateView(UpdateView):
    model = questionnaire.models.Pair
    fields = ['ident']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse_lazy('questionnaire:pair_list')


# confirm the deletion of a Pair
class PairDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = questionnaire.models.Pair
    success_url = reverse_lazy('questionnaire:pair_list')

    def test_func(self):
        return self.request.user.is_staff


# shows a selected Pair
class PairDetailView(UserPassesTestMixin, LoginRequiredMixin, DetailView):
    model = questionnaire.models.Pair
    context_object_name = 'pair'

    def get_context_data(self, **kwargs):
        pseudo_users = PseudoUser.objects.filter(pair__exact=self.object)
        context = super().get_context_data(**kwargs)
        context['pseudo_user'] = PseudoUser.objects.filter(pair__exact=self.object)
        if pseudo_users.count() >= 1:
            context['questionnaires_user_one'] = QuestionnaireDaily.objects.filter(pseudo_user__exact=pseudo_users[0])
        if pseudo_users.count() >= 2:
            context['questionnaires_user_two'] = QuestionnaireDaily.objects.filter(pseudo_user__exact=pseudo_users[1])
        return context

    def test_func(self):
        return self.request.user.is_staff


# creates a new DailyQuestionnaire
class CreateDailyQuestionnaireView(LoginRequiredMixin, CreateView):
    model = questionnaire.models.QuestionnaireDaily
    fields = ['question_one', 'question_two', 'question_three', 'question_four', 'question_five', 'question_six']
    template_name = 'questionnaire/questionnaire_daily_form.html'
    success_url = reverse_lazy('questionnaire:landing_page')

    # fügt dem Formular den aufrufenden PseudoUser hinzu
    def form_valid(self, form):
        messages.success(self.request, f"Fragebogen gespeichert")
        form.instance.created_by = self.request.user
        form.instance.pseudo_user = self.request.user
        return super().form_valid(form)

    # Overrides the get method, view can only be called under certain conditions
    def get(self, *args, **kwargs):
        daily_questionnaires = QuestionnaireDaily.objects.filter(
            pseudo_user__exact=self.request.user)
        start_questionnaire = QuestionnaireStart.objects.filter(
            pseudo_user__exact=self.request.user)

        for dq in daily_questionnaires:
            if dq.date == datetime.date.today():
                redirect("questionnaire:landing_page")

        if start_questionnaire.count() == 0:
            return redirect("questionnaire:landing_page")
        if not daily_questionnaires.filter(date__contains=datetime.date.today(),
                                           date__startswith=datetime.date.today()):
            return super(CreateDailyQuestionnaireView, self).get(*args, **kwargs)

        return redirect("questionnaire:landing_page")


class CreateStartQuestionnaireView(LoginRequiredMixin, CreateView):
    model = questionnaire.models.QuestionnaireStart
    # fields = ['question_one', 'question_two', 'question_three', 'question_four', 'question_five', 'question_six']
    form_class = questionnaire.forms.QuestionnaireStartForm
    template_name = 'questionnaire/questionnaire_start_form.html'
    success_url = reverse_lazy('questionnaire:landing_page')

    # fügt dem Formular den aufrufenden PseudoUser hinzu und ändert das Gesxchlecht
    def form_valid(self, form):
        print(form)
        form.instance.pseudo_user = self.request.user
        pseudo_user = self.request.user
        pseudo_user.gender = self.request.POST['gender']
        print(self.request.POST['gender'])
        pseudo_user.save()
        messages.success(self.request, f"Fragebogen gespeichert")
        return super().form_valid(form)

    # Overrides the get method, view can only be called under certain conditions
    def get(self, *args, **kwargs):
        if QuestionnaireStart.objects.filter(pseudo_user__exact=self.request.user):
            return redirect("questionnaire:landing_page")
        else:
            return super(CreateStartQuestionnaireView, self).get(*args, **kwargs)


class CreateEndQuestionnaireView(LoginRequiredMixin, CreateView):
    model = questionnaire.models.QuestionnaireEnd
    fields = ['question_one', 'question_two', 'question_three', 'question_four', 'question_five', 'question_six']
    template_name = 'questionnaire/questionnaire_end_form.html'
    success_url = reverse_lazy('questionnaire:landing_page')

    # fügt dem Formular den aufrufenden PseudoUser hinzu
    def form_valid(self, form):
        form.instance.pseudo_user = self.request.user
        messages.success(self.request, f"Fragebogen gespeichert")
        return super().form_valid(form)

    # Overrides the get method, view can only be called under certain conditions
    def get(self, *args, **kwargs):
        if QuestionnaireDaily.objects.filter(pseudo_user__exact=self.request.user).count() < 60:
            return redirect("questionnaire:landing_page")
        if QuestionnaireEnd.objects.filter(pseudo_user__exact=self.request.user).exists():
            return redirect("questionnaire:landing_page")

        return super(CreateEndQuestionnaireView, self).get(*args, **kwargs)
