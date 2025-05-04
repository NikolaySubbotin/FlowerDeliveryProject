from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'total_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'city', 'street')
    inlines = [OrderItemInline]
    actions = ['mark_processing', 'mark_completed', 'mark_cancelled']

    @admin.action(description='Отметить как «В обработке»')
    def mark_processing(self, request, queryset):
        count = queryset.update(status='processing')
        self.message_user(request, f"{count} заказ(ов) отмечено как «В обработке»")

    @admin.action(description='Отметить как «Выполнен»')
    def mark_completed(self, request, queryset):
        count = queryset.update(status='completed')
        self.message_user(request, f"{count} заказ(ов) отмечено как «Выполнен»")

    @admin.action(description='Отметить как «Отменён»')
    def mark_cancelled(self, request, queryset):
        count = queryset.update(status='cancelled')
        self.message_user(request, f"{count} заказ(ов) отмечено как «Отменён»")