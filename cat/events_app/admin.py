from django.contrib import admin
from django.core.checks import messages
from django.utils.safestring import mark_safe

from .models import *


admin.site.site_header = "KOT - Администрирование"
admin.site.site_title = "Admin"
admin.site.index_title = "KOT - Admin"



@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cat', 'loc', 'is_active', 'display_logo')
    fields = ['id', 'idfull', 'slug_name', 'date_start', 'date_end', 'anons', 'logo', 'display_logo', 'min_price', 'max_price', 'is_free', 'views_count', 'creator', 'is_active', 'is_by_user']
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)
    readonly_fields = ('id', 'slug_name', 'display_logo')
    list_filter = ('is_active', 'cat', 'loc', 'pref')
    actions = ['deactivate_events', 'activate_events']
    list_per_page = 20
    save_on_top = True


    @admin.display(description='Логотип')
    def display_logo(self, event: Events):
        if event.logo:
            return mark_safe(f'<img src="{event.logo.url}" width=150>')
        else:
            return 'Логотип не обнаружен'

    @admin.action(description='Деактивировать выбранные события')
    def deactivate_events(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, 'События деактивированы', messages.WARNING)


    @admin.action(description='Активировать выбранные события')
    def activate_events(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, 'События активированы', messages.INFO)

@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug_name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)


@admin.register(Profiles)
class ProfilesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)


@admin.register(Locations)
class LocationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug_name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)
