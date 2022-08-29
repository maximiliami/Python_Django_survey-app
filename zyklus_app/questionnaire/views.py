import datetime

from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.views.decorators.cache import cache_control
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic.detail import SingleObjectMixin

import questionnaire
from service.services import Service
from .models import PseudoUser, Pair, \
    Questionnaire, Answer, Choice, Question, QuestionCatalogue
from .forms import QuestionChoiceFormset


# Create your views here.
# logical process
@login_required(login_url='/')
def landing_page(request):
    # fetches the user from the database
    if request.user.is_authenticated:
        pseudo_user = get_object_or_404(PseudoUser, pk=request.user.pk)
        daily_questionnaires = Questionnaire.objects.filter(
            pseudo_user__exact=request.user, is_start_questionnaire=False,
            is_end_questionnaire=False)  # fetches all DailyQuestionnaires of this user

        # fetches questionnaire_/ -start and -end
        questionnaire_start = Questionnaire.objects.filter(pseudo_user__exact=request.user,
                                                           is_start_questionnaire=True,
                                                           is_end_questionnaire=False)
        if questionnaire_start.count() == 0:
            questionnaire_start = None
        questionnaire_end = Questionnaire.objects.filter(pseudo_user__exact=request.user,
                                                         is_end_questionnaire=True,
                                                         is_start_questionnaire=False)
        if questionnaire_end.count() == 0:
            questionnaire_end = None

        # render admin interface if Staff or Superuser
        if request.user.is_superuser or request.user.is_staff:

            return admin_interface(request)
        else:
            # Program flow for normal users
            # render create_sq if the Users questionnaire_start is None
            if questionnaire_start is None:
                return redirect('questionnaire:create_questionnaire', which_quest='start')

            if daily_questionnaires.count() < Service.PERIOD:
                # tests whether a dq has already been created today
                if not daily_questionnaires.filter(date__contains=datetime.date.today(),
                                                   date__startswith=datetime.date.today()):
                    return redirect('questionnaire:create_questionnaire', which_quest='daily')
                else:
                    if Questionnaire.objects.filter(pseudo_user__exact=request.user,
                                                    is_start_questionnaire=False,
                                                    is_end_questionnaire=False).count() != 0:
                        dq_count = Questionnaire.objects.filter(pseudo_user__exact=request.user,
                                                                is_start_questionnaire=False,
                                                                is_end_questionnaire=False).count()
                    else:
                        dq_count = 0
                    if Questionnaire.objects.filter(pseudo_user__exact=request.user,
                                                    is_start_questionnaire=True):
                        sq = Questionnaire.objects.filter(pseudo_user__exact=request.user,
                                                          is_start_questionnaire=True)[0].date.date()
                    else:
                        sq = 'Noch nicht abgeschlossen'
                    if Questionnaire.objects.filter(pseudo_user__exact=request.user,
                                                    is_end_questionnaire=True,
                                                    is_start_questionnaire=False):
                        lq = Questionnaire.objects.filter(pseudo_user__exact=request.user,
                                                          is_start_questionnaire=False,
                                                          is_end_questionnaire=True)[0].date.date()
                    else:
                        lq = 'Noch nicht abgeschlossen'
                    context = {'page_title': 'User Interface',
                               'pseudo_user': pseudo_user,
                               'dq_count': dq_count,
                               'sq': sq,
                               'lq': lq,
                               }
                    return render(request, 'questionnaire/dq_already.html', context)

            if questionnaire_end is None:
                return redirect('questionnaire:create_questionnaire', which_quest='end')

            # Todo render success page
            context = {'page_title': 'Vielen Dank!', 'pseudo_user': pseudo_user}
            return render(request, 'questionnaire/success.html', context)
    else:
        return redirect('member:login')


# downloads the data of a pair
@staff_member_required(login_url='questionnaire:landing_page')
def download_pair_data(request, pk):
    return Service.download_data_service(pk)


# downloads the data of a pair excluding start- an end-questionnaire
@staff_member_required(login_url='questionnaire:landing_page')
def download_all_data(request):
    return Service.download_data_service(None)


@login_required(login_url='questionnaire:landing_page')
def admin_interface(request):
    members = PseudoUser.objects.all()
    question_catalogues = QuestionCatalogue.objects.all()
    pairs = Pair.objects.all()
    context = {'page_title': 'Admin-interface',
               'members': members,
               'pairs': pairs,
               'question_catalogues': question_catalogues}
    return render(request, 'questionnaire/admin_interface.html', context)


# creates a new Pair
class CreatePairView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = questionnaire.models.Pair
    fields = ['ident']
    template_name = 'questionnaire/pair_form.html'
    success_url = 'pair_list'
    login_url = 'member:login'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('questionnaire:landing_page')


# shows a list of Pairs
class PairListView(UserPassesTestMixin, LoginRequiredMixin, ListView):
    model = questionnaire.models.Pair
    ordering = 'ident'

    def get_context_data(self, **kwargs):
        pseudo_users = PseudoUser.objects.all()

        context = super().get_context_data(**kwargs)
        context['pseudo_users'] = pseudo_users
        return context

    def test_func(self):
        return self.request.user.is_staff


# changes a Pair
@method_decorator(login_required, name='dispatch')
class PairUpdateView(UpdateView):
    model = questionnaire.models.Pair
    fields = ['ident']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse_lazy('questionnaire:landing_page')


# confirm the deletion of a Pair
class PairDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = questionnaire.models.Pair

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('questionnaire:landing_page')


# shows a selected Pair
@method_decorator(login_required, name='dispatch')
class PairDetailView(UserPassesTestMixin, LoginRequiredMixin, DetailView):
    model = questionnaire.models.Pair
    context_object_name = 'pair'

    def get_context_data(self, **kwargs):
        pseudo_users = PseudoUser.objects.filter(pair__exact=self.object)
        context = super().get_context_data(**kwargs)
        context['pseudo_user'] = PseudoUser.objects.filter(pair__exact=self.object)
        if pseudo_users.count() >= 1:
            context['questionnaires_user_one'] = Questionnaire.objects.filter(pseudo_user__exact=pseudo_users[0],
                                                                              is_start_questionnaire=False,
                                                                              is_end_questionnaire=False)
        if pseudo_users.count() >= 2:
            context['questionnaires_user_two'] = Questionnaire.objects.filter(pseudo_user__exact=pseudo_users[1],
                                                                              is_start_questionnaire=False,
                                                                              is_end_questionnaire=False)
        return context

    def test_func(self):
        return self.request.user.is_staff


class CreateChoice(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = questionnaire.models.Choice
    form_class = questionnaire.forms.QuestionForm
    template_name = 'questionnaire/question_form.html'
    success_url = 'landing_page'
    login_url = 'member:login'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        success_url = '../../question/' + str(self.object.pk) + '/choice/edit'
        return success_url


@method_decorator([never_cache, login_required], name='dispatch')
class CreateQuestion(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = questionnaire.models.Question
    form_class = questionnaire.forms.QuestionForm
    template_name = 'questionnaire/question_form.html'
    login_url = 'member:login'

    def form_valid(self, form):
        context = self.get_context_data()
        choices = context['choices']
        with transaction.atomic():
            form.instance.question_catalogue = QuestionCatalogue.objects.filter(name=self.kwargs['which_catalogue'])[0]
            print(self.kwargs)
            form.instance.created_by = self.request.user
            self.object = form.save()
        return super(CreateQuestion, self).form_valid(form)

    def get_context_data(self, **kwargs):
        data = super(CreateQuestion, self).get_context_data(**kwargs)
        data['which_catalogue'] = QuestionCatalogue.objects.filter(name=self.kwargs['which_catalogue'])[0]
        if self.request.POST:
            data['choices'] = QuestionChoiceFormset(self.request.POST)
        else:
            data['choices'] = QuestionChoiceFormset()
        return data

    def get_success_url(self):
        success_url = '../../question/' + str(self.object.pk) + '/choice/edit'
        return success_url

    def test_func(self):
        return self.request.user.is_staff


class QuestionDeleteView(DeleteView, UserPassesTestMixin, LoginRequiredMixin):
    model = Question

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        success_url = '../questionnaire_catalogue/' + self.object.question_catalogue.name
        return success_url


class QuestionDetailView(DetailView, UserPassesTestMixin, LoginRequiredMixin):
    model = Question
    template_name = 'questionnaire/question_detail.html'

    def test_func(self):
        return self.request.user.is_staff


@method_decorator([never_cache, login_required], name='dispatch')
class QuestionChoiceUpdateView(SingleObjectMixin, FormView, UserPassesTestMixin, LoginRequiredMixin):
    model = Question
    template_name = 'questionnaire/question_choice_edit.html'

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Question.objects.all())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Question.objects.all())
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        return QuestionChoiceFormset(**self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Änderungen gespeichert')

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        success_url = '../../../questionnaire_catalogue/' + self.object.question_catalogue.name
        return success_url


@login_required(login_url='questionnaire:landing_page')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_catalogue(request, which_questionnaire):
    question_catalogue = QuestionCatalogue.objects.filter(name__exact=which_questionnaire)
    questions = question_catalogue[0].get_all_questions()
    context = {'page_title': 'Admin-interface',
               'question_catalogue': question_catalogue[0],
               'questions': questions}
    return render(request, 'questionnaire/question_catalogue.html', context)


@login_required(login_url='questionnaire:landing_page')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_questionnaire(request, which_quest):
    regular_questions = []
    question_catalogue = QuestionCatalogue.objects.filter(name=which_quest)
    questions = question_catalogue[0].get_all_questions()

    for question in questions:
        if not Choice.objects.filter(question=question).count() <= 0:
            regular_questions.append(question)

    if which_quest == 'test':
        page_title = 'Test Fragebogen'
    elif which_quest == 'start':
        if check_for_start_questionnaire(request):
            return redirect("questionnaire:landing_page")
        page_title = 'Start Fragebogen'
    elif which_quest == 'daily':
        if check_for_today_questionnaire(request):
            return redirect('questionnaire:landing_page')
        page_title = 'Täglicher Fragebogen'
    elif which_quest == 'end':
        if Questionnaire.objects.filter(pseudo_user__exact=request.user,
                                        is_end_questionnaire=False,
                                        is_start_questionnaire=False).count() < Service.PERIOD or \
                Questionnaire.objects.filter(
                    pseudo_user__exact=request.user,
                    is_end_questionnaire=True):
            return redirect('questionnaire:landing_page')
        page_title = 'Letzter Fragebogen'
    else:
        page_title = 'Fehler 404'

    if questions.count() == 0:
        return render(request, 'questionnaire/no_questions.html')

    return render(request, 'questionnaire/questionnaire_form.html',
                  {'questions': regular_questions, 'page_title': page_title, 'quest': which_quest})


@login_required(login_url='questionnaire:landing_page')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def save_quest(request, which_quest):
    questions = Question.objects.filter(question_catalogue__name=which_quest)
    question_list = []
    answer_list = []
    get_choices = []
    regular_questions = []

    for question in questions:
        get_choices.append(question.get_all_choices())

    if which_quest == 'start':
        quest = Questionnaire(pseudo_user=request.user)
        quest.is_start_questionnaire = True
        quest.gender = request.POST['gender']
        pseudo_user = request.user
        pseudo_user.gender = request.POST['gender']
        pseudo_user.save()
    elif which_quest == 'daily':
        quest = Questionnaire(pseudo_user=request.user)
    elif which_quest == 'end':
        quest = Questionnaire(pseudo_user=request.user)
        quest.is_end_questionnaire = True
    else:
        quest = Questionnaire(pseudo_user=request.user)
    quest.save()

    for question in questions:
        if not Choice.objects.filter(question=question).count() <= 0:
            regular_questions.append(question)

    for question in regular_questions:
        question_name = request.POST[question.name]
        question_list.append(question_name)
        answer_text = Choice.objects.filter(question=question, value=question_name)[0]
        answer = Answer(pseudo_user=request.user, value=question_name, answer_text=answer_text, questionnaire=quest)
        answer_list.append(answer)
        answer.save()

    messages.success(request, 'Fragebogen gespeichert')

    # return redirect('questionnaire:landing_page')
    return redirect('questionnaire:landing_page')


def check_for_today_questionnaire(request):
    daily_questionnaires = Questionnaire.objects.filter(
        pseudo_user__exact=request.user,
        is_start_questionnaire=False,
        is_end_questionnaire=False)
    if daily_questionnaires.filter(date__contains=datetime.date.today(),
                                   date__startswith=datetime.date.today()):
        return True
    return False


def check_for_start_questionnaire(request):
    start_questionnaire = Questionnaire.objects.filter(
        pseudo_user__exact=request.user, is_start_questionnaire=True)
    print(start_questionnaire)
    if start_questionnaire.count() == 0:
        return False
    else:
        return True
