from django.urls import path
from questionnaire.views import *

app_name = "questionnaire"

urlpatterns = [
    path('create_pair', CreatePairView.as_view(extra_context={'page_title': 'Neues Paar'}), name='create_pair'),
    path('download/<pk>', download_pair_data, name='download'),
    path('download_all_data', download_all_data, name='download_all_data'),
    path('pair_list', PairListView.as_view(extra_context={'page_title': 'Paarliste'}), name='pair_list'),
    path('update_pair/<pk>', PairUpdateView.as_view(
        extra_context={'page_title': 'Paar ändern'}), name='update_pair'),
    path('delete_pair/<pk>', PairDeleteView.as_view(
        extra_context={'page_title': 'Paar löschen'}), name='delete_pair'),
    path('pair_detail/<pk>/', PairDetailView.as_view(
        extra_context={'page_title': 'Paar'}), name='pair_detail'),
    path('create_dq', CreateDailyQuestionnaireView.as_view(extra_context={'page_title': 'Täglicher Fragebogen'}),
         name='create_dq'),
    path('landing_page', landing_page, name='landing_page'),
    path('create_sq', CreateStartQuestionnaireView.as_view(extra_context={'page_title': '"erster" Fragebogen'}),
         name='create_sq'),
    path('create_eq', CreateEndQuestionnaireView.as_view(extra_context={'page_title': '"letzter" Fragebogen'}),
         name='create_eq'),
    path('create_tq/<which_quest>', show_questionnaire, name='create_tq'),
    path('save_q/<which_quest>', save_quest, name='save_q'),
]
