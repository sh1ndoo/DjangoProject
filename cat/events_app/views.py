from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Events, Profiles
import requests

cats = [
    {'url': 'events', 'name': 'События'},
]

profile_obj = Profiles.objects.get(url='ifknow')

def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>NOT THERE</h1>')

def profile(request, profile_url):
    base_data = {'profile': profile_obj,
                 'cat_selected': 'profile'}
    return render(request, 'events_app/profile.html', base_data)

def login(request):
    return render(request, 'events_app/login.html')

def home_page(request):
    qs = Events.objects.filter(cat_id=1011)[:20].values()
    list_of_dicts = list(qs)
    data = {'events': list_of_dicts,
            'cat_selected': 'events',
            'profile': profile_obj,
            'cat_url': requests.get('https://aleatori.cat/random.json').json()['url']
            }
    return render(request, 'events_app/poster.html', data)

def event(request, event_name):
    event = get_object_or_404(Events, slug_name=event_name)
    base_data = {'event': event,
                 'profile': profile_obj,
                 'cat_selected': 'events'
                 }
    return render(request, 'events_app/event.html', base_data)

