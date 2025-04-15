from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from taggit.models import Tag

from .models import Events, Profiles, Categories
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

def events(request):
    data = {'events': Events.objects.all()[:20],
            'cat_selected': 'events',
            'event_cat_selected': 'vse',
            'profile': profile_obj,
            'cat_url': requests.get('https://aleatori.cat/random.json').json()['url'],
            'event_cats': Categories.objects.all(),
            'event_tags': Tag.objects.all()
            }
    return render(request, 'events_app/poster.html', data)

def event(request, event_name):
    event = get_object_or_404(Events, slug_name=event_name)
    print(event.places[0])
    base_data = {'event': event,
                 'profile': profile_obj,
                 'cat_selected': 'events'
                 }
    return render(request, 'events_app/event.html', base_data)


def category(request, category_name):
    if category_name == 'vse':
        return redirect('events')
    cat = get_object_or_404(Categories, slug_name=category_name)
    data = {'events': Events.objects.filter(cat=cat)[:20],
            'cat_selected': 'events',
            'event_cat_selected': category_name,
            'profile': profile_obj,
            'cat_url': requests.get('https://aleatori.cat/random.json').json()['url'],
            'event_cats': Categories.objects.all(),
            'event_tags': Tag.objects.all()
            }
    return render(request, 'events_app/poster.html', data)


def home_page(request):
    return redirect('events')