from unicodedata import category

from django.urls import path

from .views import *

urlpatterns = [
    path('profile/<slug:profile_url>', profile, name='profile'),
    path('login/', login, name='login'),
    path('events/', events, name='events'),
    path('event/<slug:event_name>', event, name='event'),
    path('category/<slug:category_name>', category, name='category'),
    path('', home_page, name='home'),
]