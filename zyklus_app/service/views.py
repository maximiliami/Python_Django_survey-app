from django.shortcuts import render


# subscribe to Web-Push-group
def subscribe(request):
    webpush = {"group": "daily"}
    return render(request, 'service/subscribe.html', {"webpush": webpush})
