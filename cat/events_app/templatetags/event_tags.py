from django import template
import events_app.views as views

register = template.Library()


@register.simple_tag
def f():
    return views.data


@register.inclusion_tag('events_app/includes/header.html')
def show_header(cat_selected, profile=None):
    data = views.cats
    return {'data': data, 'cat_selected': cat_selected, 'profile': profile}