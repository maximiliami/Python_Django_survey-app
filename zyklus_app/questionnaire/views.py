from django.shortcuts import HttpResponse


# Create your views here.
def index(request):
    name = request.GET.get('name') or 'world'
    return HttpResponse(f'Hello {name}, you look beautiful today!')
