import cat.settings as settings  # Preserving original settings import
from django.conf import settings as django_settings  # For YANDEX_MAPS_API_KEY if cat.settings is not Django settings
from django.core.cache import cache
from django.db.models import F
from django.http import HttpResponse, Http404, HttpResponseNotFound  # HttpResponse needed for PageNotFoundHandlerView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, RedirectView
from django.views.generic.edit import CreateView

from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta  # Consolidated datetime imports
import requests
import json
from taggit.models import Tag

from .forms import EventCreateForm
from .models import Events, Categories, Addresses
from .utils import GlobalContextMixin

# profile_obj = Profiles.objects.get(url='ifknow')

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
    cache_timeout = 3600  # 1 час

    combined_data = cache.get(cache_key)

    if combined_data is None:
        combined_data = []
        today_date = date.today()
        current_start_date = date(start_year, start_month, 1)
        day_abbrs_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        for i in range(num_months):
            year = current_start_date.year
            month = current_start_date.month

            if i > 0:
                month_name = get_month_name_ru(month)
                if month_name:
                    combined_data.append({
                        'type': 'separator',
                        'month_name': month_name,
                        'year': year
                    })

            temp_date = date(year, month, 1)
            while temp_date.month == month:
                weekday_index = temp_date.weekday()
                is_weekend = weekday_index >= 5
                is_inactive = temp_date < today_date

                combined_data.append({
                    'type': 'date',
                    'number': temp_date.day,
                    'day_name': day_abbrs_ru[weekday_index],
                    'is_weekend': is_weekend,
                    'is_inactive': is_inactive,
                    'date_str': temp_date.strftime('%Y-%m-%d'),
                    'month': month,
                    'year': year
                })
                temp_date += timedelta(days=1)
            current_start_date += relativedelta(months=1)
        cache.set(cache_key, combined_data, cache_timeout)
    return combined_data


# Error Handler View
class PageNotFoundHandlerView(View):
    """
    Class-based view to handle 404 errors.
    To be used with handler404 in urls.py:
    handler404 = 'your_app.views.PageNotFoundHandlerView.as_view()'
    """

    def dispatch(self, request, *args, **kwargs):
        return HttpResponseNotFound('<h1>NOT THERE</h1>')





# Class-Based Views
class HomePageView(RedirectView):
    pattern_name = 'events'

class EventsView(RedirectView):
    url = '/category/'

class AboutView(TemplateView):
    template_name = 'events_app/about.html'

class ProfileView(GlobalContextMixin, TemplateView):
    page_title = 'Профиль'
    template_name = 'events_app/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # profile_url = self.kwargs.get('profile_url') # Available if needed for specific profile logic
        context['cat_selected'] = 'profile'
        return context

class EventsListView(GlobalContextMixin, ListView):
    page_title = 'КОТ - События'
    model = Events
    template_name = 'events_app/poster.html'
    context_object_name = 'events'

    # queryset = Events.objects.all()[:20] # Alternative to overriding get_queryset

    def get_queryset(self):
        return Events.objects.all()[:20]  # Preserves original slicing

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today_date = date.today()
        current_year = today_date.year
        current_month = today_date.month
        context['combined_data'] = get_combined_dates_data(current_year, current_month, num_months=3)
        context['cat_selected'] = 'events'
        context['event_cat_selected'] = None
        # try:
        #     response = requests.get('https://api.thecatapi.com/v1/images/search')
        #     response.raise_for_status()  # Raise an exception for HTTP errors
        #     context['cat_url'] = response.json()[0]['url']
        # except (requests.RequestException, IndexError, KeyError, json.JSONDecodeError) as e:
        #     context['cat_url'] = None  # Fallback in case of API error
        context['event_cats'] = Categories.objects.all()
        context['event_tags'] = Tag.objects.all()
        return context


class EventDetailView(GlobalContextMixin, DetailView):
    model = Events
    template_name = 'events_app/event.html'
    context_object_name = 'event'
    slug_field = 'slug_name'
    slug_url_kwarg = 'event_name'
    event = None

    def get_object(self, queryset=None):
        global event
        obj = super().get_object(queryset)
        event = obj.name
        Events.objects.filter(pk=obj.pk).update(views_count=F('views_count') + 1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cat_selected'] = 'events'
        context['title'] = event
        context['yandex_api_key'] = django_settings.YANDEX_MAPS_API_KEY  # Or cat.settings.YANDEX_MAPS_API_KEY
        return context


class CategoryEventsListView(GlobalContextMixin, ListView):
    model = Events
    cat_selected = 'events'
    template_name = 'events_app/poster.html'
    context_object_name = 'events'

    paginate_by = 20

    # def dispatch(self, request, *args, **kwargs):
    #     if self.kwargs['category_name'] is None:
    #         return redirect('events')
    #     return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.kwargs['category_name'] is None:
            return Events.objects.all()[:20]
        category_name_slug = self.kwargs['category_name']
        self.category_instance = get_object_or_404(Categories, slug_name=category_name_slug)
        return Events.objects.filter(cat=self.category_instance)[:20]  # Preserves original slicing

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today_date = date.today()
        current_year = today_date.year
        current_month = today_date.month
        context['title'] = 'КОТ - ' + self.category_instance.name
        context['combined_data'] = get_combined_dates_data(current_year, current_month, num_months=3)
        context['event_cat_selected'] = self.kwargs['category_name']
        # try:
        #     response = requests.get('https://api.thecatapi.com/v1/images/search')
        #     response.raise_for_status()
        #     context['cat_url'] = response.json()[0]['url']
        # except (requests.RequestException, IndexError, KeyError, json.JSONDecodeError) as e:
        #     context['cat_url'] = None
        context['event_cats'] = Categories.objects.all()
        context['event_tags'] = Tag.objects.all()
        return context


class EventCreateView(GlobalContextMixin, CreateView):
    model = Events
    form_class = EventCreateForm
    template_name = 'events_app/create_event.html'

    def get_success_url(self):
        return reverse('profile', kwargs={'profile_url': 'ifknow'})

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()

        is_form_valid = form.is_valid()
        print(is_form_valid, form.errors)

        if is_form_valid:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        event_instance = form.save(commit=False)

        # Custom logic from original FBV
        event_instance.id = str(datetime.now().timestamp()).replace('.', '')
        event_instance.loc_id = 718  # Overrides form selection for 'loc' field.

        event_instance.save()
        self.object = event_instance

        address_obj = Addresses.objects.create(
            address=form.cleaned_data['address'],
            name=form.cleaned_data['address_name'],
            city=form.cleaned_data['address_city'],
            description=form.cleaned_data['address_description']
        )
        self.object.addresses.add(address_obj)
        form.save_m2m()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cat_selected'] = 'profile'
        context['yandex_api_key'] = django_settings.YANDEX_MAPS_API_KEY  # Or cat.settings.YANDEX_MAPS_API_KEY
        return context