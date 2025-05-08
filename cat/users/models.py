from django.contrib.auth.models import AbstractUser
from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit, Transpose



class User(AbstractUser):
    avatar = ProcessedImageField(verbose_name='Логотип', blank=True, null=True,
                               processors=[
                                            Transpose(), # Исправляет ориентацию по EXIF (важно!)
                                            ResizeToFit(width=300, upscale=False) # Макс. ширина 1920px, не увеличивать маленькие
                                          ],
                               format='WEBP', # Или 'WEBP'
                               options={'quality': 80}, default='base_event_logo.webp')
    phone = models.CharField(max_length=12, unique=True, blank=True, null=True)
    background_img = models.TextField(blank=True, null=True)
    rating = models.FloatField(blank=True, default=0.0)
    address = models.TextField(blank=True, null=True)
    likes = models.TextField(blank=True, null=True)
    reviews = models.TextField(blank=True, null=True)
    events = models.TextField(blank=True, null=True)
    about = models.CharField(max_length=50, blank=True, null=True, default='Пользователь ничего не написал')
    views_count = models.IntegerField(blank=True, default=0)

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'