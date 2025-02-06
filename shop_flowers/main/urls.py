from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="main/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
]


