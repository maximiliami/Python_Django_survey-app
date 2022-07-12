from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, DetailView, UpdateView, CreateView

# Create your views here.
from questionnaire.forms import RegisterForm, UpdateUserForm
import questionnaire.models


# logs a user in
def login_user(request):
    context = {'page_title': 'Login'}
    context_logged_in = {'page_title': 'Test'}

    if request.user.is_authenticated:
        return render(request, 'questionnaire/test.html', context_logged_in)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {username}")
            return redirect('questionnaire:landing_page')
        else:
            messages.error(request, "There was an error!")
            return redirect('/', context)
    else:
        return render(request, 'authenticate/login.html', context)


# logs a user out
def logout_view(request):
    logout(request)


# change password view
class PasswordsChangeView(PasswordChangeView):
    template_name = 'authenticate/change-password.html'
    success_url = reverse_lazy('questionnaire:landing_page')
    success_message = 'Passwort erfolgreich geändert'

    def form_valid(self, form):
        messages.success(self.request, 'Passwort erfolgreich geändert')
        return super().form_valid(form)


# creates a new PseudoUser
class CreateMemberView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    form_class = RegisterForm
    template_name = 'questionnaire/pseudouser_form.html'
    success_url = 'member_list'
    login_url = 'member:login'

    def test_func(self):
        return self.request.user.is_staff


# changes a PseudoUser
class MemberUpdateView(UpdateView):
    form_class = UpdateUserForm
    model = questionnaire.models.PseudoUser
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse_lazy('member:member_list')


# shows a list of PseudoUser
class MemberListView(UserPassesTestMixin, LoginRequiredMixin, ListView):
    model = questionnaire.models.PseudoUser
    ordering = 'user_code'

    def test_func(self):
        return self.request.user.is_staff


# confirm the deletion of a PseudoUser
class MemberDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = questionnaire.models.PseudoUser
    success_url = reverse_lazy('member:member_list')

    def test_func(self):
        return self.request.user.is_staff


# shows a selected PseudoUser
class MemberDetailView(UserPassesTestMixin, LoginRequiredMixin, DetailView):
    model = questionnaire.models.PseudoUser

    def get_context_data(self, **kwargs):
        daily_questionnaires = questionnaire.models.QuestionnaireDaily.objects.filter(pseudo_user__exact=self.object)
        start_questionnaire = questionnaire.models.QuestionnaireStart.objects.filter(pseudo_user__exact=self.object)
        end_questionnaire = questionnaire.models.QuestionnaireEnd.objects.filter(pseudo_user__exact=self.object)

        context = super().get_context_data(**kwargs)
        context['dq'] = len(daily_questionnaires)
        context['start_questionnaire'] = start_questionnaire
        context['end_questionnaire'] = end_questionnaire
        context['pseudo_user'] = self.object
        return context

    def test_func(self):
        return self.request.user.is_staff
