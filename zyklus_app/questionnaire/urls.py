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
    path('landing_page', landing_page, name='landing_page'),
    path('create_questionnaire/<which_quest>', create_questionnaire, name='create_questionnaire'),
    path('save_q/<which_quest>', save_quest, name='save_q'),
    path('create_question/<which_catalogue>/', CreateQuestion.as_view(extra_context={'page_title': 'Neue Frage'}),
         name='create_question'),
    path('questionnaire_catalogue/<which_questionnaire>', show_catalogue, name='questionnaire_catalogue'),
    path('question/<int:pk>', QuestionDetailView.as_view(), name='question_detail'),
    path('question/<int:pk>/choice/edit', QuestionChoiceUpdateView.as_view(), name='question_update'),
    path('delete_question/<pk>', QuestionDeleteView.as_view(
        extra_context={'page_title': 'Frage löschen'}), name='delete_question'),
]
