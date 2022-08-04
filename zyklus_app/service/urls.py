from django.urls import path

import service.views

app_name = "service"

urlpatterns = [
    path('subscribe', service.views.subscribe, name='subscribe'),
]
