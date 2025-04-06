from django.urls import path

from .views import *

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('login/', login, name='login'),
    path('', home_page, name='home'),
]