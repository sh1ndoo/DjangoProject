from django.db import models
from django.template.defaultfilters import slugify
from random import randint

from django.urls import reverse
from unidecode import unidecode

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



# Create your models here.
