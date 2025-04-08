from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse

data = {'data': [
    {'name': 'Борат', 'genre': 'Прикол'},
    {'name': 'Борат', 'genre': 'Прикол'},
    {'name': 'Борат', 'genre': 'Прикол'},
    {'name': 'Борат', 'genre': 'Прикол'},
    {'name': 'Борат', 'genre': 'Прикол'},
    {'name': 'Борат', 'genre': 'Прикол'},
    {'name': 'Борат', 'genre': 'Прикол'}],
}

cats = [
    {'url': 'profile', 'name': 'Профиль'},
    {'url': 'events', 'name': 'События'},
]



def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>NOT THERE</h1>')

def profile(request):
    data['cat_selected'] = 'profile'
    return render(request, 'events_app/profile.html', data)

def login(request):
    return render(request, 'events_app/login.html', data)

def home_page(request):
    data['cat_selected'] = 'events'
    return render(request, 'events_app/poster.html', data)

