from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('phone', 'first_name', 'email', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('phone', 'first_name', 'email')
    ordering = ('phone',)

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'phone',
                    'first_name',
                    'email',
                    'password1',
                    'password2',
                    'is_active',
                    'is_staff',
                ),
            },
        ),
    )
