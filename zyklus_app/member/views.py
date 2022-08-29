from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, DetailView, UpdateView, CreateView
from django.views.decorators.cache import cache_control
# Create your views here.
from questionnaire.forms import RegisterForm, UpdateUserForm
from questionnaire.models import PseudoUser, Questionnaire


# logs a user in
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_user(request):
    context = {'page_title': 'Login'}
    context_logged_in = {'page_title': 'Test'}

    if request.user.is_authenticated:
        return redirect('questionnaire:landing_page')

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
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    logout(request)
    return redirect('member:login')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_user(request):
    return render(request, 'authenticate/logout.html')


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

    def get_success_url(self):
        return reverse_lazy('questionnaire:landing_page')


# changes a PseudoUser
class MemberUpdateView(UpdateView):
    form_class = UpdateUserForm
    model = PseudoUser
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse_lazy('questionnaire:landing_page')


# shows a list of PseudoUser
class MemberListView(UserPassesTestMixin, LoginRequiredMixin, ListView):
    model = PseudoUser
    ordering = 'user_code'

    def test_func(self):
        return self.request.user.is_staff


# confirm the deletion of a PseudoUser
class MemberDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = PseudoUser
    success_url = reverse_lazy('member:member_list')

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('questionnaire:landing_page')


# shows a selected PseudoUser
class MemberDetailView(UserPassesTestMixin, LoginRequiredMixin, DetailView):
    model = PseudoUser

    def get_context_data(self, **kwargs):
        daily_questionnaires = Questionnaire.objects.filter(pseudo_user__exact=self.object,
                                                            is_end_questionnaire=False,
                                                            is_start_questionnaire=False)
        start_questionnaire = Questionnaire.objects.filter(pseudo_user__exact=self.object,
                                                           is_end_questionnaire=False,
                                                           is_start_questionnaire=False)
        end_questionnaire = Questionnaire.objects.filter(pseudo_user__exact=self.object,
                                                         is_end_questionnaire=False,
                                                         is_start_questionnaire=False)

        context = super().get_context_data(**kwargs)
        context['dq'] = len(daily_questionnaires)
        context['start_questionnaire'] = start_questionnaire
        context['end_questionnaire'] = end_questionnaire
        context['pseudo_user'] = self.object
        return context

    def test_func(self):
        return self.request.user.is_staff
