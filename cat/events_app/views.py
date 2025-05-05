import base64
from datetime import datetime
from random import randint
import cat.settings as settings
from django.db.models import F
from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from taggit.models import Tag
import json
import datetime
import calendar
from django.shortcuts import render
from django.core.cache import cache
from dateutil.relativedelta import relativedelta

from .forms import EventCreateForm
from .models import Events, Profiles, Categories, Addresses
import requests

cats = [
    {'url': 'events', 'name': 'События'},
]

profile_obj = Profiles.objects.get(url='ifknow')

def get_month_name_ru(month):
    """Возвращает русское название месяца."""
    months_ru = [
        "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    if 1 <= month <= 12:
        return months_ru[month]
    return ""

def get_combined_dates_data(start_year, start_month, num_months=3):
    """
    Готовит единый список словарей дат и разделителей месяцев
    для передачи в шаблон. Кэширует результат.
    """
    cache_key = f'combined_dates_data_{start_year}_{start_month}_{num_months}'
    # Время жизни кэша (например, 1 час, т.к. is_inactive зависит от today)
    cache_timeout = 3600

    combined_data = cache.get(cache_key)

    if combined_data is None:
        print(f"Cache miss for combined data {start_year}-{start_month} (+{num_months} mo). Generating.") # Отладка
        combined_data = []
        today = datetime.date.today()
        current_start_date = datetime.date(start_year, start_month, 1)
        day_abbrs_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        for i in range(num_months):
            year = current_start_date.year
            month = current_start_date.month

            # Добавляем разделитель ПЕРЕД данными месяца (кроме первого)
            if i > 0:
                month_name = get_month_name_ru(month)
                if month_name:
                    combined_data.append({
                        'type': 'separator', # Маркер типа
                        'month_name': month_name,
                        'year': year
                    })

            # Генерируем даты для текущего месяца
            temp_date = datetime.date(year, month, 1)
            while temp_date.month == month:
                weekday_index = temp_date.weekday()
                is_weekend = weekday_index >= 5
                is_inactive = temp_date < today

                combined_data.append({
                    'type': 'date', # Маркер типа
                    'number': temp_date.day,
                    'day_name': day_abbrs_ru[weekday_index],
                    'is_weekend': is_weekend,
                    'is_inactive': is_inactive,
                    'date_str': temp_date.strftime('%Y-%m-%d'),
                    'month': month,
                    'year': year
                })
                temp_date += datetime.timedelta(days=1)

            # Переходим к следующему месяцу
            current_start_date += relativedelta(months=1)

        # Сохраняем результат в кэш
        cache.set(cache_key, combined_data, cache_timeout)
    else:
         print(f"Cache hit for combined data {start_year}-{start_month} (+{num_months} mo).") # Отладка

    return combined_data





def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>NOT THERE</h1>')

def profile(request, profile_url):
    base_data = {'profile': profile_obj,
                 'cat_selected': 'profile'}
    return render(request, 'events_app/profile.html', base_data)

def login(request):
    return render(request, 'events_app/login.html')

def events(request):
    today = datetime.date.today()
    current_year = today.year
    current_month = today.month
    combined_data = get_combined_dates_data(current_year, current_month, num_months=3)

    data = {'events': Events.objects.all()[:20],
            'cat_selected': 'events',
            'event_cat_selected': None,
            'profile': profile_obj,
            'cat_url': requests.get('https://api.thecatapi.com/v1/images/search').json()[0]['url'],
            'event_cats': Categories.objects.all(),
            'event_tags': Tag.objects.all(),
            'combined_data': combined_data,  # Передаем единый список
            }
    return render(request, 'events_app/poster.html', data)

def event(request, event_name):
    event = get_object_or_404(Events, slug_name=event_name)
    Events.objects.filter(slug_name=event_name).update(views_count= F('views_count') + 1)
    base_data = {'event': event,
                 'profile': profile_obj,
                 'cat_selected': 'events',
                 'yandex_api_key': settings.YANDEX_MAPS_API_KEY,
                 }
    a = render(request, 'events_app/event.html', base_data)
    return a


def category(request, category_name):
    if category_name == 'vse':
        return redirect('events')
    cat = get_object_or_404(Categories, slug_name=category_name)
    today = datetime.date.today()
    current_year = today.year
    current_month = today.month
    combined_data = get_combined_dates_data(current_year, current_month, num_months=3)
    data = {'events': Events.objects.filter(cat=cat)[:20],
            'cat_selected': 'events',
            'event_cat_selected': category_name,
            'profile': profile_obj,
            'cat_url': requests.get('https://api.thecatapi.com/v1/images/search').json()[0]['url'],
            'event_cats': Categories.objects.all(),
            'event_tags': Tag.objects.all(),
            'combined_data': combined_data,  # Передаем единый список
            }
    return render(request, 'events_app/poster.html', data)

def create_event(request):
    if request.method == 'POST':
        form = EventCreateForm(request.POST, request.FILES)
        print(form.is_valid(), form.errors)
        if form.is_valid():
            eventt = form.save(commit=False)
            eventt.id = str(datetime.datetime.now().timestamp()).replace('.', '')
            eventt.loc_id = 718
            eventt.save()
            a = Addresses.objects.create(address=form.cleaned_data['address'], name=form.cleaned_data['address_name'], city=form.cleaned_data['address_city'], description=form.cleaned_data['address_description'])
            eventt.addresses.add(a)
            eventt.save()
            form.save_m2m()
            return redirect('profile', profile_url='ifknow')
    else:
        form = EventCreateForm()

    base_data = {'profile': profile_obj,
                 'cat_selected': 'profile',
                 'form': form,
                 'yandex_api_key': settings.YANDEX_MAPS_API_KEY,}
    return render(request, 'events_app/create_event.html', base_data)


def home_page(request):
    return redirect('events')