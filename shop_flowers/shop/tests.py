from django.test import TestCase
from .models import Order, OrderItem, Bouquet
from django.contrib.auth import get_user_model

class OrderModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(username="testuser")

        # Создаем тестовые букеты с ценами
        self.bouquet1 = Bouquet.objects.create(name="Розы", price=500)
        self.bouquet2 = Bouquet.objects.create(name="Лилии", price=1000)

        # Создаем заказ
        self.order = Order.objects.create(user=self.user, status="pending")

        # Добавляем товары в заказ
        OrderItem.objects.create(order=self.order, product=self.bouquet1, quantity=2)  # 500 * 2 = 1000
        OrderItem.objects.create(order=self.order, product=self.bouquet2, quantity=1)  # 1000 * 1 = 1000

        # Пересчитываем общую стоимость заказа
        self.order.update_total_price()

    def test_order_total_price(self):
        expected_price = (self.bouquet1.price * 2) + (self.bouquet2.price * 1)  # 500*2 + 1000*1 = 2000
        self.assertEqual(self.order.total_price, expected_price)