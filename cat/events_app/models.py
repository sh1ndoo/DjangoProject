from django.db import models
from django.template.defaultfilters import slugify
from random import randint
import datetime
from django.urls import reverse
from unidecode import unidecode

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
class Events(models.Model):
    id = models.IntegerField(primary_key=True)
    idfull = models.CharField(max_length=20)
    pref = models.CharField(max_length=10)
    cat_id = models.IntegerField()
    cat_url = models.CharField(max_length=50)
    loc_id = models.IntegerField()
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
    places = models.TextField()
    slug_name = models.CharField(max_length=200, blank=True)


    def save_slug(self, *args, **kwargs):
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
        month = russian_months[date_obj.month - 1]  # Индекс на 1 меньше номера месяца
        year = date_obj.year
        hour = date_obj.hour
        minute = date_obj.minute
        formatted_date = f"{day} {month} {year} в {hour:02d}:{minute:02d}"
        return formatted_date

    def __str__(self):
        return self.name




class Profiles(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=500, default="")
    phone = models.CharField(max_length=12, default="")
    password = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
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




