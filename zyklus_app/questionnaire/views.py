from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from .models import PseudoUser


# Create your views here.
@login_required(login_url='/')
def test(request):
    context = {'page_title': 'Login'}
    return render(request, 'questionnaire/test.html', context)


class PseudoUserListView(ListView):
    model = PseudoUser
