from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem, Order, OrderItem
from .forms import CartAddForm
from flowers.models import Bouquet
import logging

logger = logging.getLogger(__name__)

@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        form = CartAddForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Количество обновлено")
    return redirect('cart')

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})


@login_required
def cart_view(request):
    # Получаем корзину текущего пользователя или создаем новую
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.cart_items.all()

    # Передаем корзину в шаблон
    return render(request, 'shop/cart.html', {'cart': cart, 'items': items})

@login_required
def add_to_cart(request, bouquet_id):
    bouquet = get_object_or_404(Bouquet, id=bouquet_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=bouquet,
        defaults={'quantity': 1}
    )
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"Букет «{bouquet.name}» добавлен в корзину!")
    return redirect('cart')


@login_required
def remove_from_cart(request, item_id):
    """Удаление товара из корзины"""
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, "Товар удален из корзины")
    return redirect('cart')


@login_required
def order_history(request):
    # Забираем только свои заказы, подгружаем товары одним запросом
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related('items__product')
        .order_by('-created_at')
    )
    return render(request, 'shop/order_history.html', {
        'orders': orders
    })

@login_required
def create_order(request):
    try:
        with transaction.atomic():  # Для атомарности операции
            # Получаем корзину пользователя
            cart = get_object_or_404(Cart, user=request.user)

            if not cart.cart_items.exists():
                messages.warning(request, "Ваша корзина пуста!")
                return redirect('cart')

            # Создаем заказ
            order = Order.objects.create(
                user=request.user,
                city=request.POST.get("city"),
                street=request.POST.get("street"),
                house_number=request.POST.get("house_number"),
                apartment_number=request.POST.get("apartment_number"),
                status='new'
            )

            # Переносим товары из корзины в заказ
            total_price = 0
            for cart_item in cart.cart_items.all():
                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity
                )
                total_price += order_item.total_price()

            order.total_price = total_price
            order.save()

            # Очищаем корзину
            cart.cart_items.all().delete()
            cart.delete()

            messages.success(request, f"Заказ №{order.id} успешно оформлен!")

            print(f"Создан заказ: {order.id}, {order.user}, {order.status}, {order.total_price}")
            return redirect('order_success')

    except Exception as e:
        messages.error(request, f"Ошибка при оформлении заказа: {str(e)}")
        return redirect('cart')


def reorder(request, order_id):
    old_order = get_object_or_404(Order, id=order_id, user=request.user)
    # создаём новый заказ, копируя поля адреса из старого
    new_order = Order.objects.create(
        user=request.user,
        city=old_order.city,
        street=old_order.street,
        house_number=old_order.house_number,
        apartment_number=old_order.apartment_number or '',
        status='new',
    )
    # копируем все элементы заказа
    for item in old_order.items.all():
        OrderItem.objects.create(
            order=new_order,
            product=item.product,
            quantity=item.quantity
        )
    # пересчитываем общую сумму
    new_order.update_total_price()
    messages.success(request, "Заказ успешно повторен!")
    return redirect('order_history')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.cart_items.all()
    if request.method == 'POST':
        city           = request.POST['city']
        street         = request.POST['street']
        house_number   = request.POST['house_number']
        apartment_num  = request.POST.get('apartment_number', '')

        if not (city and street and house_number):
            messages.error(request, "Пожалуйста, заполните все обязательные поля адреса.")
            return redirect('checkout')

        order = Order.objects.create(
            user=request.user,
            city=city,
            street=street,
            house_number=house_number,
            apartment_number=apartment_num,
            status='new'
        )
        total = 0
        for ci in items:
            OrderItem.objects.create(order=order, product=ci.product, quantity=ci.quantity)
            total += ci.product.price * ci.quantity

        order.total_price = total
        order.save()

        cart.cart_items.all().delete()
        messages.success(request, "Спасибо! Ваш заказ оформлен.")
        return redirect('order_history')

    # GET — показываем форму
    return render(request, 'shop/checkout.html', {
        'total_price': cart.total_price(),
    })


@login_required
def order_success(request):
    return render(request, "shop/order_success.html")