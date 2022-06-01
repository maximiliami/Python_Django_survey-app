from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Create your views here.
def login_user(request):
    context = {'page_title': 'Login'}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/', context)
        else:
            messages.error(request, "There was an error!")
            return redirect('/', context)
    else:
        return render(request, 'authenticate/login.html', context)
