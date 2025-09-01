from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum

from .models import (Berry, Cake, ClickCounter, Courier, Decoration, Form,
                     Level, Order, Topping, PromoCode)


@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'form',
        'levels',
        'topping',
        'is_show',
        'text'
    ]

    readonly_fields = ['price']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['amount', 'price']
    list_display_links = ['amount']
    search_fields = ['amount']
    ordering = ['amount']


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    list_display_links = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    list_display_links = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Berry)
class BerryAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    list_display_links = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Decoration)
class DecorationAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    list_display_links = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'rating']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'order_notes', 'cost']
    list_filter = ['delivery_date', 'courier']
    readonly_fields = ['cost', 'created_at']

    fieldsets = (
        ('Информация о заказе', {
            'fields': ('status', 'user', 'cake', 'courier', 'cost'),
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


@admin.register(ClickCounter)
class ClickCounterAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'clicks', 'referral_link')
    readonly_fields = ('clicks', 'referral_link', 'token')
    search_fields = ('token',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ['clicks']

    def referral_link(self, obj):
        url = f"{settings.SITE_URL}/?ref={obj.token}"
        return format_html(
            '<input type="text" value="{}" readonly style="width: 300px;" onclick="this.select()">'
            '<br><a href="{}" target="_blank">Перейти по ссылке</a>',
            url, url
        )

    referral_link.short_description = "Реферальная ссылка"


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'orders_count', 'orders_sum')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _orders_count=Count('orders', distinct=True),
            _orders_sum=Sum('orders__cost')
        )

    def orders_count(self, obj):
        return obj._orders_count or 0
    orders_count.short_description = 'Кол-во заказов'

    def orders_sum(self, obj):
        return obj._orders_sum or 0
    orders_sum.short_description = 'Сумма заказов'