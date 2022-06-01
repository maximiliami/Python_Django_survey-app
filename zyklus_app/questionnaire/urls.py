from django.urls import path

import questionnaire.views
from . import views

urlpatterns = [
    path('', 'login'),
]
