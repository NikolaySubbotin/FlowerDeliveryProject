from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('create-order/', views.create_order, name='create_order'),
    path('checkout/', views.checkout, name='checkout'),
    path("order-history/", views.order_history, name="order_history"),  # История заказов
    path("reorder/<int:order_id>/", views.reorder, name="reorder"),  # Повторный заказ
    path('order_success/', views.order_success, name='order_success'),
]