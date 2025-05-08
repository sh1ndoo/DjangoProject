from django import template
import events_app.views as views
from events_app import utils

register = template.Library()


@register.inclusion_tag('events_app/includes/header.html')
def show_header(cat_selected, user=None):
    data = utils.cats
    return {'data': data, 'cat_selected': cat_selected, 'user': user}