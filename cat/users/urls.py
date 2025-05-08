from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView


app_name = 'users'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('registration/', views.UserRegistrationView.as_view(), name='registration'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('<slug:username>/', views.UserDetailView.as_view(), name='user_detail'),
    path('<slug:username>/update/', views.UserUpdateView.as_view(), name='user_update'),

]