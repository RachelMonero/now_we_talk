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
    path('profile/',views.profile, name='profile'),
    path('profile_update/', views.profile_update, name='profile_update'),
    path('contact/', views.contact, name='contact' ),

]