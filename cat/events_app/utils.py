from django.views import View

# from events_app.models import Profiles

cats = [
    {'url': 'events', 'name': 'События'},
]

# profile_obj = Profiles.objects.get(url='ifknow')


class GlobalContextMixin(View):
    """
    Mixin to add globally used context data like profile_obj.
    """
    page_title = None
    cat_selected = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['profile'] = profile_obj
        context['cats_menu'] = cats # 'cats' global var could be added here if needed widely
        if self.page_title is not None:
            context['title'] = self.page_title
        context['cat_selected'] = self.cat_selected
        return context