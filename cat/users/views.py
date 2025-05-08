from django import forms

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView, LogoutView
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, UpdateView, DetailView

from events_app.utils import GlobalContextMixin
from .forms import LoginUserForm, RegisterUserForm, UpdateUserForm

User = get_user_model()

class UserLoginView(GlobalContextMixin, LoginView):
    authentication_form = LoginUserForm
    template_name = 'users/login.html'
    page_title = 'Авторизация'
    # next_page = reverse_lazy('events')

    def get_success_url(self):
        user = self.request.user
        return reverse('users:user_detail', args=[user.username])



class UserRegistrationView(GlobalContextMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'users/registration.html'
    page_title = 'Регистрация'
    # success_url = reverse_lazy('events')

    def get_success_url(self):
        user = self.object
        return reverse('users:user_detail', args=[user.username])
#
#
class UserDetailView(GlobalContextMixin, DetailView):
    template_name = 'users/profile.html'
    page_title = 'Профиль'
    model = User
    context_object_name = 'user'
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserUpdateView(GlobalContextMixin, UpdateView):
    template_name = 'users/user_update.html'
    page_title = 'Профиль - редактирование'
    model = User
    form_class = UpdateUserForm
    slug_field = 'username'
    slug_url_kwarg = 'username'


    # context_object_name = 'user'
    # slug_field = 'username'
    # slug_url_kwarg = 'username'


    def get_success_url(self):
         # Получаем объект пользователя, который был только что сохранен
         # self.object доступен в get_success_url
         return reverse_lazy('users:user_detail', kwargs={'username': self.request.user.username}) # Пример, если у вас есть Profile с полем url


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')

# class UserPasswordChangeView(PasswordChangeView):
#     form_class = UserPasswordChangeForm
#     template_name = 'users/password_change.html'
#     success_url = reverse_lazy('users:password_change_done')
#     title = 'Изменение пароля'