from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem, Order, OrderItem
from .forms import CartAddForm
from flowers.models import Bouquet


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

    # Передаем корзину в шаблон
    return render(request, 'shop/cart.html', {'cart': cart})

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
    """История заказов"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'shop/order_history.html', {'orders': orders})

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
                delivery_address=request.user.address,
                status='new'
            )

            # Переносим товары из корзины в заказ
            for cart_item in cart.cart_items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity
                )

            # Очищаем корзину
            cart.cart_items.all().delete()

            messages.success(request, f"Заказ №{order.id} успешно оформлен!")
            return redirect('order_success')

    except Exception as e:
        messages.error(request, f"Ошибка при оформлении заказа: {str(e)}")
        return redirect('cart')


def reorder(request, order_id):
    old_order = get_object_or_404(Order, id=order_id, user=request.user)

    # Создаем новый заказ и копируем данные
    new_order = Order.objects.create(
        user=request.user,
        status='pending',
        delivery_address=old_order.delivery_address  # Копируем адрес доставки
    )

    # Копируем товары из старого заказа
    new_order.products.set(old_order.products.all())

    messages.success(request, "Заказ успешно повторен!")
    return redirect("order_history")  # Перенаправляем в историю заказов

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)

    if not cart_items:
        return redirect('cart')  # Если корзина пуста, отправляем пользователя обратно

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            status="pending",  # Начальный статус заказа
            total_price=total_price,
            delivery_address="Адрес по умолчанию"  # Временно, можно обновить позже
        )

        # Добавляем товары в заказ
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        # Очищаем корзину после оформления заказа
        cart_items.delete()

        return redirect('order_success')

    return render(request, 'shop/checkout.html', {"total_price": total_price})

def order_success(request):
    """Отображает страницу успешного оформления заказа"""
    return render(request, 'shop/order_success.html')