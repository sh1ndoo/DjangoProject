import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, UserChangeForm
from django.views.generic import UpdateView

User = get_user_model()


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'avatar', 'username']

        widgets = {
            'avatar': forms.FileInput(attrs={
                'hidden': True,
                'id': 'avatar'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Никнейм'
            }),

        }




class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин/email', widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Логин/email'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Пароль'}))

    class Meta:
        model = get_user_model()


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(label='*E-mail', widget=forms.EmailInput(attrs={'class': 'form-input'}))

    password1 = forms.CharField(
        label='*Пароль',
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password",
                                          'class': 'form-input'}),
    )
    password2 = forms.CharField(
        label='*Повторите пароль',
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password",
                                          'class': 'form-input'}),
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': '*Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия'
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        model = User
        if model.objects.filter(email=email).exists():
            raise forms.ValidationError(f'Пользователь с email: {email} уже зарегистрирован')
        return email
#
#
# class ProfileUserForm(forms.ModelForm):
#     username = forms.CharField(disabled=True, label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
#     email = forms.CharField(disabled=True, required=False, label='E-mail', widget=forms.TextInput(attrs={'class': 'form-input'}))
#     this_year = datetime.date.today().year
#     date_birth = forms.DateField(label='Дата рождения', widget=forms.SelectDateWidget(years=tuple(range(this_year - 100, this_year - 5))))
#
#     class Meta:
#         model = get_user_model()
#         fields = ['username', 'email', 'first_name', 'last_name']
#         labels = {
#             'first_name': 'Имя',
#             'last_name': 'Фамилия',
#         }
#         widgets = {
#             'first_name': forms.TextInput(attrs={'class': 'form-input'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-input'}),
#         }
#
#
# class UserPasswordChangeForm(PasswordChangeForm):
#     old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
#     new_password1 = forms.CharField(label="Новый пароль",
#                                     widget=forms.PasswordInput(attrs={'class': 'form-input', 'id': 'id_password1'}))
#     new_password2 = forms.CharField(label="Повторите пароль",
#                                     widget=forms.PasswordInput(attrs={'class': 'form-input', 'id': 'id_password2'}))