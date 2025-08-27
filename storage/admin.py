from django.contrib import admin

from .models import Courier, Order


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'rating']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'order_notes']
    list_filter = ['delivery_date', 'courier']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Информация о заказе', {
            'fields': ('user', 'cake', 'courier', 'cost'),
            'description': 'Основные данные заказа'
        }),
        ('Доставка', {
            'fields': ('address', 'delivery_date', 'delivery_time'),
            'description': 'Информация о доставке'
        }),
        ('Примечания', {
            'fields': ('order_notes', 'delivery_notes'),
            'classes': ('collapse',),
            'description': 'Дополнительные заметки к заказу'
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',),
            'description': 'Техническая информация'
        }),
    )
