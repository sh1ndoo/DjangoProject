# from unicodedata import category
#
# from django.urls import path
#
# from .views import *
#
# urlpatterns = [
#     path('profile/<slug:profile_url>', profile, name='profile'),
#     path('login/', login, name='login'),
#     path('events/', events, name='events'),
#     path('event/<slug:event_name>', event, name='event'),
#     path('category/<slug:category_name>', category, name='category'),
#     path('create_event', create_event, name='create_event'),
#     path('', home_page, name='home'),
# ]




from django.urls import path
from .views import (
    ProfileView,
    EventsListView,
    EventDetailView,
    CategoryEventsListView,
    EventCreateView,
    HomePageView,
    PageNotFoundHandlerView, AboutView, EventsView  # Import the custom 404 handler view
)

urlpatterns = [
    path('events/', EventsView.as_view(), name='events'),
    path('event/<slug:event_name>', EventDetailView.as_view(), name='event'),
    path('category/<slug:category_name>', CategoryEventsListView.as_view(), name='category'),
    path('create_event', EventCreateView.as_view(), name='create_event'),
    path('about', AboutView.as_view(), name='about'),
    path('', HomePageView.as_view(), name='home'),
]