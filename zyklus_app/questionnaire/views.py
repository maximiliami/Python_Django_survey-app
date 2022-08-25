import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views.decorators.cache import cache_control
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib import messages

import questionnaire
from service.services import Service
from .models import PseudoUser, QuestionnaireDaily, QuestionnaireStart, QuestionnaireEnd, Pair, \
    QuestionnaireTest, Answer, Choice, QuestionnaireTestStart
from .forms import QuestionnaireStartForm


# Create your views here.
# logical process
@login_required(login_url='/')
def landing_page(request):
    # fetches the user from the database
    if request.user.is_authenticated:
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
            members = PseudoUser.objects.all()
            pairs = Pair.objects.all()
            context = {'page_title': 'Admin-interface', 'members': members, 'pairs': pairs}
            return admin_interface(request, context)
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
                    if QuestionnaireDaily.objects.filter(pseudo_user__exact=request.user).count() != 0:
                        dq_count = QuestionnaireDaily.objects.filter(pseudo_user__exact=request.user).count()
                    else:
                        dq_count = 0
                    if QuestionnaireStart.objects.filter(pseudo_user__exact=request.user):
                        sq = QuestionnaireStart.objects.filter(pseudo_user__exact=request.user)[0].date.date()
                    else:
                        sq = 'Noch nicht abgeschlossen'
                    if QuestionnaireEnd.objects.filter(pseudo_user__exact=request.user):
                        lq = QuestionnaireEnd.objects.filter(pseudo_user__exact=request.user)[0].date.date()
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
                return redirect('questionnaire:create_eq')

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
def admin_interface(request, context):
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
        return reverse_lazy('questionnaire:pair_list')


# confirm the deletion of a Pair
class PairDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = questionnaire.models.Pair
    success_url = reverse_lazy('questionnaire:pair_list')

    def test_func(self):
        return self.request.user.is_staff


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
            context['questionnaires_user_one'] = QuestionnaireDaily.objects.filter(pseudo_user__exact=pseudo_users[0])
        if pseudo_users.count() >= 2:
            context['questionnaires_user_two'] = QuestionnaireDaily.objects.filter(pseudo_user__exact=pseudo_users[1])
        return context

    def test_func(self):
        return self.request.user.is_staff


# creates a new DailyQuestionnaire
@method_decorator([never_cache, login_required], name='dispatch')
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


@method_decorator([never_cache, login_required], name='dispatch')
class CreateStartQuestionnaireView(LoginRequiredMixin, CreateView):
    model = questionnaire.models.QuestionnaireStart
    # fields = ['question_one', 'question_two', 'question_three', 'question_four', 'question_five', 'question_six']
    form_class = questionnaire.forms.QuestionnaireStartForm
    template_name = 'questionnaire/questionnaire_start_form.html'
    success_url = reverse_lazy('questionnaire:landing_page')

    # fügt dem Formular den aufrufenden PseudoUser hinzu und ändert das Geschlecht
    def form_valid(self, form):
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


@method_decorator([never_cache, login_required], name='dispatch')
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


def test_for_print(request):
    max = PseudoUser.objects.filter(user_code__exact='max')
    ##
    test_quests = QuestionnaireTestStart.objects.filter(pseudo_user=max[0])
    index = 0

    for quest in test_quests:
        ## Gets id for content_type_query
        test_questionnaire = ContentType.objects.get_for_model(QuestionnaireTestStart)
        answers = Answer.objects.filter(content_type__pk=test_questionnaire.id, object_id__exact=quest.id)

        print(quest)
        for a in answers:
            print(a.answer_text)
            print(a.object_id)
        index += 1


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_questionnaire(request, which_quest):
    questions = Service.get_questions_for_catalogue_by_id(request,
                                                          Service.get_question_catalogue_id(request, which_quest))

    if which_quest == 'test':
        page_title = 'Test Fragebogen'
    elif which_quest == 'start':
        page_title = 'Start Fragebogen'
    elif which_quest == 'daily':
        page_title = 'Täglicher Fragebogen'
    elif which_quest == 'end':
        page_title = 'Letzter Fragebogen'
    else:
        page_title = 'Fehler 404'

    if questions.count() == 0:
        ## TODO Template keine Fragen angelegt
        return redirect('questionnaire:landing_page')

    return render(request, 'questionnaire/questionnaire_form.html',
                  {'questions': questions, 'page_title': page_title, 'quest': which_quest})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def save_quest(request, which_quest):
    questions = Service.get_questions_for_catalogue_by_id(request, Service.get_question_catalogue_id(request, which_quest))
    question_list = []
    answer_list = []

    if which_quest == 'test':
        quest = QuestionnaireTest(pseudo_user=request.user)
    elif which_quest == 'start':
        quest = QuestionnaireTestStart(pseudo_user=request.user)
        quest.gender = request.POST['gender']
        pseudo_user = request.user
        pseudo_user.gender = request.POST['gender']
        pseudo_user.save()
    elif which_quest == 'daily':
        quest = QuestionnaireDaily(pseudo_user=request.user)
    elif which_quest == 'end':
        quest = QuestionnaireEnd(pseudo_user=request.user)
    else:
        quest = QuestionnaireTest(pseudo_user=request.user)
    quest.save()

    for question in questions:
        question_name = request.POST[question.name]
        question_list.append(question_name)
        answer_text = Choice.objects.filter(question=question, value=question_name)[0]
        answer = Answer(pseudo_user=request.user, value=question_name, answer_text=answer_text,
                        content_object=quest,
                        object_id=quest.id)
        answer_list.append(answer)
        answer.save()

    # return redirect('questionnaire:landing_page')
    return render(request, 'questionnaire/test.html',
                  {'questions': question_list, 'answer_list': answer_list, 'quest': quest})
