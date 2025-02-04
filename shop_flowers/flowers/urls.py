from django.urls import path
from . import views

urlpatterns = [
    path('', views.bouquet, name='bouquet_list'),  # Список букетов
    path('<int:pk>/', views.bouquet_detail, name='bouquet_detail'),  # Детальная страница
]