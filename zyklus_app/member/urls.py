from django.urls import path

from .views import *

# makes the app known in the application
app_name = "member"


urlpatterns = [
    path('', login_user, name="login",),
    path('login_user', login_user, name="login",),
    path('logout_user', logout_view, name="logout"),
    path('create_member', CreateMemberView.as_view(
        extra_context={'page_title': 'Neuer Benutzer'}), name='create_member'),
    path('member_list', MemberListView.as_view(
        extra_context={'page_title': 'Benutzerliste'}), name='member_list'),
    path('delete_member/<pk>', MemberDeleteView.as_view(
        extra_context={'page_title': 'Delete Member'}), name='delete_member'),
    path('member_detail/<pk>/', MemberDetailView.as_view(
        extra_context={'page_title': 'Benutzer'}), name='member_detail'),
    path('update_member/<pk>', MemberUpdateView.as_view(
        extra_context={'page_title': 'Edit Member'}), name='update_member'),
    path('password', PasswordsChangeView.as_view(), name='password')
]
