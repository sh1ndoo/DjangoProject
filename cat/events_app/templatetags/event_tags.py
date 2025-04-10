from django import template
import events_app.views as views

register = template.Library()


@register.simple_tag
def f():
    return views.data


@register.inclusion_tag('events_app/includes/header.html')
def show_header(cat_selected, *args, **kwargs):
    data = views.cats
    if args:
        url = args[0]
        return {'data': data, 'cat_selected': cat_selected, 'url': url}
    return {'data': data, 'cat_selected': cat_selected}