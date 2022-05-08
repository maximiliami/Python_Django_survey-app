from django.shortcuts import HttpResponse

from django.views.generic import ListView

from .models import PseudoUser


# Create your views here.
def index(request):
    name = request.GET.get('name') or 'world'
    return HttpResponse(f'Hello {name}, you look beautiful today!')


class PseudoUserListView(ListView):
    model = PseudoUser
