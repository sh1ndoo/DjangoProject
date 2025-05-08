import json

import requests
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from django.template.defaultfilters import slugify
from random import randint
from datetime import datetime
from django.urls import reverse
from taggit.models import Tag
from unidecode import unidecode
from taggit.managers import TaggableManager
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit, Transpose

from cat import settings

russian_months = [
    "января",  # 1
    "февраля",  # 2
    "марта",  # 3
    "апреля",  # 4
    "мая",  # 5
    "июня",  # 6
    "июля",  # 7
    "августа",  # 8
    "сентября",  # 9
    "октября",  # 10
    "ноября",  # 11
    "декабря"  # 12
]

events_count = 0





class ChildrenEventModel(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(age__in=['0+', '6+'])


class Events(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['id', 'slug_name', 'is_free']),
        ]
        default_manager_name = 'objects'
        verbose_name='Событие'
        verbose_name_plural = 'События'

    id = models.IntegerField(primary_key=True)
    idfull = models.CharField(max_length=50, verbose_name='Полное id', blank=True, null=True)
    pref = models.CharField(max_length=10, verbose_name='Источник', default='kot', blank=True)
    name = models.CharField(max_length=200, verbose_name='Название')
    date_start = models.DateTimeField(verbose_name='Дата начала')
    date_end = models.DateTimeField(verbose_name='Дата окончания')
    logo = ProcessedImageField(verbose_name='Логотип', blank=True, null=True,
                               processors=[
                                            Transpose(), # Исправляет ориентацию по EXIF (важно!)
                                            ResizeToFit(width=500, upscale=False) # Макс. ширина 1920px, не увеличивать маленькие
                                          ],
                               format='WEBP', # Или 'WEBP'
                               options={'quality': 80}, default='base_event_logo.webp')
    anons = models.TextField(verbose_name='Анонс', blank=True)
    is_free = models.BooleanField(verbose_name='Бесплатно')
    min_price = models.IntegerField(verbose_name='Минимальная цена', blank=True)
    max_price = models.IntegerField(verbose_name='Максимальная цена', blank=True)
    age = models.CharField(max_length=5, verbose_name='Возрастное ограничение')
    addresses = models.ManyToManyField('Addresses', related_name='events')
    slug_name = models.SlugField(max_length=200, blank=True, unique=True, verbose_name='Slug')
    cat = models.ForeignKey('Categories', on_delete=models.CASCADE, related_name='events', verbose_name='Категория')
    tags = TaggableManager(verbose_name='Теги', blank=True)
    loc = models.ForeignKey('Locations', on_delete=models.CASCADE, related_name='events', verbose_name='Локация')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    views_count = models.IntegerField(default=0, verbose_name='Кол-во просмотров', blank=True)
    is_by_user = models.BooleanField(default=False, verbose_name='Создано пользователем')
    # creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events', verbose_name='Создатель', blank=True, null=True)


    children = ChildrenEventModel
    objects = models.Manager


    def save(self, *args, **kwargs):
        name = unidecode(self.name)
        if self.id is not None:
            if Events.objects.filter(id=self.id).exists():
                old_event = Events.objects.get(id=self.id)
                if old_event.name != self.name:
                    self.slug_name = slugify(name) + '_' + str(datetime.now().timestamp()).replace('.', '')
            else:
                self.slug_name = slugify(name) + '_' + str(datetime.now().timestamp()).replace('.', '')
        else:
            self.slug_name = slugify(name) + '_' + str(datetime.now().timestamp()).replace('.', '')
        super().save(*args, **kwargs)

    def get_image(self):
        if self.logo_base64:
            return f'data:image/png;base64,{self.logo_base64}'
        elif self.logo:
            return self.logo

    def time_start(self):
        day = self.date_start.day
        month = russian_months[self.date_start.month - 1]  # Индекс на 1 меньше номера месяца
        year = self.date_start.year
        hour = self.date_start.hour
        minute = self.date_start.minute
        formatted_date = f"{day} {month} {year} в {hour:02d}:{minute:02d}"
        return formatted_date

    def time_end(self):
        day = self.date_end.day
        month = russian_months[self.date_end.month - 1]
        year = self.date_end.year
        hour = self.date_end.hour
        minute = self.date_end.minute
        formatted_date = f"{day} {month} {year} в {hour:02d}:{minute:02d}"
        return formatted_date

    def time_end_no_hour(self):
        day = self.date_end.day
        month = russian_months[self.date_end.month - 1]
        year = self.date_end.year
        formatted_date = f"{day} {month} {year}"
        return formatted_date

    def get_absolute_url(self):
        return reverse(
            'event',
            kwargs={'event_name': self.slug_name})

    @staticmethod
    def events_update():
        data_7 = {
            'APIKey': 'b3116332c2596701ef69',
            'loc_id': 718,
            'limit': 100,
            'offset': 0

        }
        js_data = True
        res_data = []
        while js_data:
            js_data = requests.post("https://api.afisha7.ru/v1.0/events/", data=data_7).json()['events']
            if not js_data:
                break
            res_data.extend(js_data)
            data_7['offset'] += 100
        for ev in res_data:
            active_names = Events.objects.filter(is_active=True).values_list('name', flat=True)
            if ev['name'] in active_names:
                Events.objects.filter(name=ev['name']).update(
                    idfull=ev['idfull'],
                    pref=ev['pref'],
                    date_start=datetime.fromtimestamp(int(ev['date_start'])),
                    date_end=datetime.fromtimestamp(int(ev['date_end'])),
                    anons=ev['anons'] if ev['anons'] else "",
                    logo=ev['logo'],
                    is_free=bool(int(ev['is_free'])),
                    min_price=ev['min_price'] if ev['min_price'] else 0,
                    max_price=ev['max_price'] if ev['max_price'] else 0,
                    age=ev['age'],
                    addresses=ev['places'],
                )
            else:
                Events.objects.create(
                    id=ev['id'],
                    idfull=ev['idfull'],
                    pref=ev['pref'],
                    name=ev['name'],
                    date_start=datetime.fromtimestamp(int(ev['date_start'])),
                    date_end=datetime.fromtimestamp(int(ev['date_end'])),
                    anons=ev['anons'] if ev['anons'] else "",
                    logo=ev['logo'],
                    is_free=bool(int(ev['is_free'])),
                    min_price=ev['min_price'] if ev['min_price'] else 0,
                    max_price=ev['max_price'] if ev['max_price'] else 0,
                    age=ev['age'],
                    addresses=ev['places'],
                    cat=Categories.objects.get(id=ev['cat_id']),
                    loc=Locations.objects.get(id=ev['loc_id']),
                )
        for i in Events.objects.all():
            if i.name not in [obj['name'] for obj in res_data]:
                i.is_active = False
                i.save()

    def __str__(self):
        return self.name




# class Profiles(models.Model):
#     class Meta:
#         verbose_name = 'Профиль'
#         verbose_name_plural = 'Профили'
#
#     name = models.CharField(max_length=50)
#     email = models.EmailField(max_length=500, default="", unique=True)
#     phone = models.CharField(max_length=12, default="", unique=True)
#     password = models.CharField(max_length=50)
#     url = models.SlugField(max_length=50, unique=True)
#     avatar_img = models.TextField(default="")
#     background_img = models.TextField(default="")
#     rating = models.IntegerField(default=0)
#     address = models.TextField(default="")
#     events_count = models.IntegerField(default=0)
#     reviews_count = models.IntegerField(default=0)
#     likes = models.TextField(default="")
#     reviews = models.TextField(default="")
#     users_events = models.TextField(default="")
#     views_count = models.IntegerField(default=0)
#
#     def __str__(self):
#         return self.name
#
#     def get_absolute_url(self):
#         return reverse(
#             'profile',
#             kwargs={'profile_url': self.url})


class Categories(models.Model):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    id = models.IntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=25, db_index=True)
    slug_name = models.SlugField(max_length=25, unique=True, db_index=True)
    icon = models.CharField(max_length=250, db_index=True, default="fa-solid fa-circle-info")


    def save(self, *args, **kwargs):
        name = unidecode(self.name)
        self.slug_name = slugify(name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'category',
            kwargs={'category_name': self.slug_name})


class Locations(models.Model):
    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'

    id = models.IntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=25, db_index=True)
    slug_name = models.SlugField(max_length=25, unique=True, db_index=True)


    def save(self, *args, **kwargs):
        name = unidecode(self.name)
        self.slug_name = slugify(name)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name

class Addresses(models.Model):
    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адресы'

    address = models.TextField(default="")
    description = models.TextField(default="")
    name = models.CharField(max_length=25, db_index=True)
    city = models.CharField(max_length=25, db_index=True, default='Москва')


    def save(self, *args, **kwargs):
        self.city = self.name.split(',')[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description