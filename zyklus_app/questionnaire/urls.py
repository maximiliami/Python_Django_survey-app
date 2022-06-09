from django.urls import path
from .views import *

app_name = "questionnaire"

urlpatterns = [
    path('create_pair', CreatePairView.as_view(extra_context={'page_title': 'Paar erstellen'}), name='create_pair'),
    path('pair_list', PairListView.as_view(extra_context={'page_title': 'Paarliste'}), name='pair_list'),
    path('update_pair/<pk>', PairUpdateView.as_view(
        extra_context={'page_title': 'Paar ändern'}), name='update_pair'),
    path('delete_pair/<pk>', PairDeleteView.as_view(
        extra_context={'page_title': 'Paar löschen'}), name='delete_pair'),
    path('pair_detail/<pk>/', PairDetailView.as_view(
        extra_context={'page_title': 'Paar'}), name='pair_detail'),

]
