import csv
import datetime
import itertools

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy

import questionnaire
from .models import PseudoUser, QuestionnaireDaily, QuestionnaireStart, QuestionnaireEnd, Pair
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

        # TODO Ablauf Zeit
        if daily_questionnaires.count() <= 59:
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
def download(request, pk):
    pair = Pair.objects.filter(pk=pk)
    pseudo_users = PseudoUser.objects.filter(pair__in=pair)

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{pair.get()}.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(
        ['Pärchen', 'Benutzer', 'Datum DailyQuestionnaire', 'Frage1', 'Frage2', 'Frage3', 'Frage4', 'Frage5',
         'Frage6', 'Datum StartQuestionnaire', 'Frage1', 'Frage2', 'Frage3', 'Frage4', 'Frage5', 'Frage6',
         'Datum EndQuestionnaire', 'Frage1', 'Frage2', 'Frage3', 'Frage4', 'Frage5', 'Frage6', ])

    if not pseudo_users:
        writer.writerow([pair.get(), '-', '-', '-', '-', '-', '-', '-', '-'])

    for pseudo_user in pseudo_users:
        questionnaires_daily = QuestionnaireDaily.objects.filter(pseudo_user__exact=pseudo_user)
        questionnaire_start = QuestionnaireStart.objects.filter(pseudo_user__exact=pseudo_user)
        questionnaire_end = QuestionnaireEnd.objects.filter(pseudo_user__exact=pseudo_user)

        flag = False

        if not questionnaire_end:
            flag = True

        if not questionnaires_daily:
            writer.writerow([pair.get(), pseudo_user, '-', '-', '-', '-', '-', '-', '-'])
        for questionnaire_daily in questionnaires_daily:
            if not flag:
                writer.writerow(
                    [pair.get(), pseudo_user, questionnaire_daily.date.date(), questionnaire_daily.question_one,
                     questionnaire_daily.question_two,
                     questionnaire_daily.question_three, questionnaire_daily.question_four,
                     questionnaire_daily.question_five, questionnaire_daily.question_six,
                     questionnaire_start.get().date.date(), questionnaire_start.get().question_one,
                     questionnaire_start.get().question_two, questionnaire_start.get().question_three,
                     questionnaire_start.get().question_four, questionnaire_start.get().question_five,
                     questionnaire_start.get().question_six, questionnaire_end.get().date.date(),
                     questionnaire_end.get().question_one, questionnaire_end.get().question_two,
                     questionnaire_end.get().question_three,
                     questionnaire_end.get().question_four, questionnaire_end.get().question_five,
                     questionnaire_end.get().question_six]),
            else:
                writer.writerow(
                    [pair.get(), pseudo_user, questionnaire_daily.date.date(), questionnaire_daily.question_one,
                     questionnaire_daily.question_two,
                     questionnaire_daily.question_three, questionnaire_daily.question_four,
                     questionnaire_daily.question_five, questionnaire_daily.question_six,
                     questionnaire_start.get().date.date(), questionnaire_start.get().question_one,
                     questionnaire_start.get().question_two, questionnaire_start.get().question_three,
                     questionnaire_start.get().question_four, questionnaire_start.get().question_five,
                     questionnaire_start.get().question_six, '-', '-', '-', '-', '-', '-', '-']),

    return response


# downloads the data of a pair excluding start- an end-questionnaire
@staff_member_required(login_url='questionnaire:landing_page')
def download_all_data(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="Zyklus-qpp-data.csv"'},
    )

    writer = csv.writer(response)

    pairs = Pair.objects.all()
    pseudo_users = PseudoUser.objects.all()
    start_questionnaires = QuestionnaireStart.objects.all()
    daily_questionnaires = QuestionnaireDaily.objects.all()
    end_questionnaires = QuestionnaireEnd.objects.all()

    for pair in pairs:
        pair_users = pseudo_users.filter(pair=pair)
        print(f'pair_users = {pair_users.count()}')
        if pair_users.count() == 2:
            pair_user_one = pair_users[0]
            pair_user_two = pair_users[1]

            pair_user_one_questionnaires = daily_questionnaires.filter(pseudo_user__exact=pair_user_one)
            pair_user_two_questionnaires = daily_questionnaires.filter(pseudo_user__exact=pair_user_two)

            writer.writerow(
                ['Pärchen', 'Benutzer1', 'Datum DailyQuestionnaire', f'F1 P1 {pair_user_one.gender}',
                 f'F2 P1 {pair_user_one.gender}',
                 f'F3 P1 {pair_user_one.gender}',
                 f'F4 P1 {pair_user_one.gender}', f'F5 P1 {pair_user_one.gender}', f'F6 P1 {pair_user_one.gender}',
                 'Benutzer2', 'Datum DailyQuestionnaire',
                 f'F1 P2 {pair_user_two.gender} ', f'F2 P2 {pair_user_two.gender}', f'F3 P2 {pair_user_two.gender}',
                 f'F4 P2 {pair_user_two.gender}', f'F5 P2 {pair_user_two.gender}', f'F6 P2 {pair_user_two.gender}'])

            for (dq_user_one, dq_user_two) in itertools.zip_longest(pair_user_one_questionnaires,
                                                                    pair_user_two_questionnaires):
                print(f'(Ausgangswert: {dq_user_one}, {dq_user_two})')
                if dq_user_one is None:
                    dq_user_one = QuestionnaireDaily(pseudo_user=PseudoUser(user_code='Default'))
                    dq_user_one.date = datetime.datetime.today()
                    dq_user_one.question_one = 'Kein Wert'
                    dq_user_one.question_two = 'Kein Wert'
                    dq_user_one.question_three = 'Kein Wert'
                    dq_user_one.question_four = 'Kein Wert'
                    dq_user_one.question_five = 'Kein Wert'
                    dq_user_one.question_six = 'Kein Wert'
                if dq_user_two is None:
                    dq_user_two = QuestionnaireDaily(pseudo_user=PseudoUser(user_code='Default'))
                    dq_user_two.date = datetime.datetime.today()
                    dq_user_two.question_one = 'Kein Wert'
                    dq_user_two.question_two = 'Kein Wert'
                    dq_user_two.question_three = 'Kein Wert'
                    dq_user_two.question_four = 'Kein Wert'
                    dq_user_two.question_five = 'Kein Wert'
                    dq_user_two.question_six = 'Kein Wert'

                print(f'({dq_user_two}, {dq_user_one})')
                writer.writerow([pair.ident, pair_user_one.user_code, dq_user_one.date.date(),
                                 dq_user_one.question_one, dq_user_one.question_two, dq_user_one.question_three,
                                 dq_user_one.question_four, dq_user_one.question_five, dq_user_one.question_six,
                                 pair_user_two.user_code, dq_user_two.date.date(), dq_user_two.question_one,
                                 dq_user_two.question_two, dq_user_two.question_three, dq_user_two.question_four,
                                 dq_user_two.question_five, dq_user_two.question_six])

    return response


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
        form.instance.created_by = self.request.user
        form.instance.pseudo_user = self.request.user
        return super().form_valid(form)

    # Overrides the get method, view can only be called under certain conditions
    def get(self, *args, **kwargs):
        daily_questionnaires = QuestionnaireDaily.objects.filter(
            pseudo_user__exact=self.request.user)

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
        return super().form_valid(form)

    # Overrides the get method, view can only be called under certain conditions
    def get(self, *args, **kwargs):
        if QuestionnaireDaily.objects.filter(pseudo_user__exact=self.request.user).count() < 30:
            return redirect("questionnaire:landing_page")
        if QuestionnaireEnd.objects.filter(pseudo_user__exact=self.request.user).exists():
            return redirect("questionnaire:landing_page")

        return super(CreateEndQuestionnaireView, self).get(*args, **kwargs)
