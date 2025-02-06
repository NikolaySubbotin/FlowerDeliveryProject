from django.conf import settings
from django.db import models
from flowers.models import Bouquet


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Используем системную настройку
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def total_price(self):
        return sum(item.total_price() for item in self.cart_items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name='cart_items',
        on_delete=models.CASCADE,
        verbose_name='Корзина'
    )
    product = models.ForeignKey(
        Bouquet,
        on_delete=models.CASCADE,
        verbose_name='Букет'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'

    def total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    delivery_address = models.TextField(verbose_name='Адрес доставки')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ {self.id} - {self.user.username}"

    @property
    def total_price(self):
        """
        Возвращает общую стоимость заказа, суммируя все элементы.
        Использует агрегацию для оптимизации запроса к базе данных.
        """
        return sum(item.total_price for item in self.items.all())

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Bouquet, through='OrderItem')  # Привязка к букетам
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    delivery_address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ {self.id} от {self.user}"


class OrderItem(models.Model):  #  Промежуточная модель между заказами и товарами
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  #  Добавлен ForeignKey к Order
    bouquet = models.ForeignKey(Bouquet, on_delete=models.CASCADE)  #  Добавлен ForeignKey к Bouquet
    quantity = models.PositiveIntegerField(default=1)  # Можно добавить количество товаров

    def __str__(self):
        return f"{self.bouquet.name} x {self.quantity} (Заказ {self.order.id})"