import json

import requests
from django.db import models
from django.template.defaultfilters import slugify
from random import randint
import datetime
from django.urls import reverse
from taggit.models import Tag
from unidecode import unidecode
from taggit.managers import TaggableManager

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

class EventTag(Tag):
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        proxy = True

    def slugify(self, tag, i=None):
        slug = unidecode(tag)
        return slugify(slug, allow_unicode=False)

class Events(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['id', 'slug_name', 'is_free', 'vip']),
        ]
        default_manager_name = 'objects'

    id = models.IntegerField(primary_key=True)
    idfull = models.CharField(max_length=20)
    pref = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    date_start = models.IntegerField()
    date_end = models.IntegerField()
    logo = models.TextField()
    logo_p = models.TextField()
    anons = models.TextField()
    is_free = models.IntegerField()
    min_price = models.IntegerField()
    max_price = models.IntegerField()
    age = models.CharField(max_length=5)
    vip = models.IntegerField()
    places = models.JSONField()
    slug_name = models.SlugField(max_length=200, blank=True, unique=True)
    cat = models.ForeignKey('Categories', on_delete=models.CASCADE, related_name='events')
    tags = TaggableManager()
    loc = models.ForeignKey('Locations', on_delete=models.CASCADE, related_name='events')
    is_active = models.BooleanField(default=True)


    children = ChildrenEventModel
    objects = models.Manager

    def save(self, *args, **kwargs):
        name = unidecode(self.name)
        self.slug_name = slugify(name) + '_' + str(randint(1, 100000))
        super().save(*args, **kwargs)

    def time_start(self):
        date_obj = datetime.datetime.fromtimestamp(self.date_start)
        day = date_obj.day
        month = russian_months[date_obj.month - 1]  # Индекс на 1 меньше номера месяца
        year = date_obj.year
        hour = date_obj.hour
        minute = date_obj.minute
        formatted_date = f"{day} {month} {year} в {hour:02d}:{minute:02d}"
        return formatted_date

    def time_end(self):
        date_obj = datetime.datetime.fromtimestamp(self.date_end)
        day = date_obj.day
        month = russian_months[date_obj.month - 1]
        year = date_obj.year
        hour = date_obj.hour
        minute = date_obj.minute
        formatted_date = f"{day} {month} {year} в {hour:02d}:{minute:02d}"
        return formatted_date

    def time_end_no_hour(self):
        date_obj = datetime.datetime.fromtimestamp(self.date_end)
        day = date_obj.day
        month = russian_months[date_obj.month - 1]
        year = date_obj.year
        formatted_date = f"{day} {month} {year}"
        return formatted_date

    def get_absolute_url(self):
        return reverse(
            'event',
            kwargs={'event_name': self.slug_name})

    def __str__(self):
        return self.name




class Profiles(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['name', 'url']),
        ]
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=500, default="", unique=True)
    phone = models.CharField(max_length=12, default="", unique=True)
    password = models.CharField(max_length=50)
    url = models.SlugField(max_length=50, unique=True)
    avatar_img = models.TextField(default="")
    background_img = models.TextField(default="")
    rating = models.IntegerField(default=0)
    address = models.TextField(default="")
    events_count = models.IntegerField(default=0)
    reviews_count = models.IntegerField(default=0)
    likes = models.TextField(default="")
    reviews = models.TextField(default="")
    users_events = models.TextField(default="")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'profile',
            kwargs={'profile_url': self.url})


class Categories(models.Model):
    id = models.IntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=25, db_index=True)
    slug_name = models.SlugField(max_length=25, unique=True, db_index=True)


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
    id = models.IntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=25, db_index=True)
    slug_name = models.SlugField(max_length=25, unique=True, db_index=True)


    def save(self, *args, **kwargs):
        name = unidecode(self.name)
        self.slug_name = slugify(name)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name




























def events_load():
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
    print(res_data)
    for ev in res_data:
        print(ev['anons'], ev['anons'] if ev['anons'] else "")
        active_names = Events.objects.filter(is_active=True).values_list('name', flat=True)
        if (ev['name'],) in active_names:
            Events.objects.filter(name=ev['name']).update(
                idfull=ev['idfull'],
                pref=ev['pref'],
                date_start=ev['date_start'],
                date_end=ev['date_end'],
                logo=ev['logo'],
                logo_p=ev['logo_p'],
                anons = ev['anons'] if ev['anons'] else "",
                is_free=ev['is_free'],
                min_price=ev['min_price'],
                max_price=ev['max_price'],
                age=ev['age'],
                vip=ev['vip'],
                places=ev['places'],
            )
        else:
            Events.objects.create(
                id=ev['id'],
                idfull=ev['idfull'],
                pref=ev['pref'],
                name=ev['name'],
                date_start=ev['date_start'],
                date_end=ev['date_end'],
                logo=ev['logo'],
                logo_p=ev['logo_p'],
                anons= ev['anons'] if ev['anons'] else "",
                is_free=ev['is_free'],
                min_price=ev['min_price'],
                max_price=ev['max_price'],
                age=ev['age'],
                vip=ev['vip'],
                places=ev['places'],
                cat=Categories.objects.get(id=ev['cat_id']),
                loc=Locations.objects.get(id=ev['loc_id']),
            )
    for i in Events.objects.all():
        if i.name not in [obj['name'] for obj in res_data]:
            i.is_active = False
            i.save()
