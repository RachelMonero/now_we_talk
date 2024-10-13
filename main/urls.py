from django.urls import path
from .views import login
from main import views

urlpatterns = [
    path('', views.login, name='login'), 
    path('login/', views.login, name='login'), 
    path('signup/',views.signup, name='signup'),
    path('pw_recovery/',views.pw_recovery, name='pw_recovery'),
    path('verification/',views.verification, name='verification'),
    path('home/',views.home, name='home'),
    path('create_chatroom/<str:friend_user_id>',views.create_chatroom, name='create_chatroom'),
]