from django.contrib import admin

from .models import Level, Form, Topping, Berry, Decoration, Cake, Courier, Order


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
