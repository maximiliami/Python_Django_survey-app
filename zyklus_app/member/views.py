from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, DetailView, UpdateView, CreateView

# Create your views here.
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
from questionnaire.forms import RegisterForm
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


# creates a new PseudoUser
class CreateMemberView(StaffuserRequiredMixin, LoginRequiredMixin, CreateView):
    form_class = RegisterForm
    template_name = 'questionnaire/pseudouser_form.html'
    success_url = 'member_list'
    login_url = 'member:login'


# shows a list of PseudoUser
class MemberListView(StaffuserRequiredMixin, LoginRequiredMixin, ListView):
    model = questionnaire.models.PseudoUser
    ordering = 'user_code'


# confirm the deletion of a PseudoUser
class MemberDeleteView(StaffuserRequiredMixin, LoginRequiredMixin, DeleteView):
    model = questionnaire.models.PseudoUser
    success_url = reverse_lazy('member:member_list')


# shows a selected PseudoUser
class MemberDetailView(StaffuserRequiredMixin, LoginRequiredMixin, DetailView):
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


# changes a PseudoUser
class MemberUpdateView(UpdateView):
    model = questionnaire.models.PseudoUser
    fields = ['user_code', 'is_active', 'pair']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse_lazy('member:member_list')
