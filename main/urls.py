from django.urls import path
from .views import add_to_myfriend, search
from main import views

urlpatterns = [
    path('', views.login, name='login'), 
    path('login/', views.login, name='login'), 
    path('signup/',views.signup, name='signup'),
    path('pw_recovery/',views.pw_recovery, name='pw_recovery'),
    path('verification/',views.verification, name='verification'),
    path('home/',views.home, name='home'),
    path('profile/',views.profile, name='profile'),
    path('profile_update/', views.profile_update, name='profile_update'),
    path('contact/', views.contact, name='contact' ),
    path('friends/', views.friends, name='friends' ),
    path('search/', views.search, name='search' ),
    path('add_to_myfriend/<uuid:user_id>', views.add_to_myfriend, name='add_to_myfriend'),
    path('open_chat/<uuid:user_id>', views.open_chat, name='open_chat'),
    path('chatroom', views.chatroom, name='chatroom'),
    path('delete_friend', views.delete_friend, name='delete_friend'),
    path('chatroom_list', views.chatroom_list, name='chatroom_list'),
    path('leave_chatroom', views.leave_chatroom, name='leave_chatroom'),
    path('create_chat/<uuid:chatroom_id>/', views.create_chat, name='create_chat'),
    path('get_audio/<uuid:chat_id>/', views.get_audio, name='get_audio'),
    path('get_voice/<uuid:chat_id>/', views.get_voice, name='get_voice'),




]