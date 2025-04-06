from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse

def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>NOT THERE</h1>')

def profile(request):
    return render(request, 'events_app/profile.html')

def login(request):
    return render(request, 'events_app/login.html')

def home_page(request):
    return render(request, 'events_app/poster.html')