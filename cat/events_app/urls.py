from django.urls import path

from .views import *

urlpatterns = [
    path('profile/<slug:profile_url>', profile, name='profile'),
    path('login/', login, name='login'),
    path('', home_page, name='events'),
    path('<slug:event_name>', event, name='event')
]