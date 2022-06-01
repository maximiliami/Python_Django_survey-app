from django.shortcuts import HttpResponse, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from .models import PseudoUser


# Create your views here.
def index(request):
    name = request.GET.get('name') or 'world'
    return HttpResponse(f'Hello {name}, you look beautiful today!')


@login_required(login_url='/')
def test(request):
    context = {'page_title': 'Login'}
    return render(request, 'questionnaire/test.html', context)


class PseudoUserListView(ListView):
    model = PseudoUser
