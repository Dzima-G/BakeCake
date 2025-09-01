from datetime import datetime, timedelta
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

from users.models import CustomUser


class Level(models.Model):
    amount = models.IntegerField(
        verbose_name='количество уровней'
    )
    price = models.DecimalField(
        verbose_name='стоимость',
        max_digits=7, decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'уровень'
        verbose_name_plural = 'уровни'

    def __str__(self):
        return str(self.amount)


class Form(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=20
    )
    price = models.DecimalField(
        verbose_name='стоимость',
        max_digits=7, decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'форма'
        verbose_name_plural = 'формы'

    def __str__(self):
        return self.name


class Topping(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=20
    )
    price = models.DecimalField(
        verbose_name='стоимость',
        max_digits=7, decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'топпинг'
        verbose_name_plural = 'топпинги'

    def __str__(self):
        return self.name


class Berry(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=20
    )
    price = models.DecimalField(
        verbose_name='стоимость',
        max_digits=7, decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'ягоды'
        verbose_name_plural = 'ягоды'

    def __str__(self):
        return self.name


class Decoration(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=20
    )
    price = models.DecimalField(
        verbose_name='стоимость',
        max_digits=7, decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'декор'
        verbose_name_plural = 'декоры'

    def __str__(self):
        return self.name


class Cake(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=50,
        default='Индивидуальный'
    )
    levels = models.ForeignKey(
        Level,
        verbose_name='количество уровней',
        on_delete=models.PROTECT,
        related_name='cakes'
    )
    form = models.ForeignKey(
        Form,
        verbose_name='форма торта',
        on_delete=models.PROTECT,
        related_name='cakes'
    )
    topping = models.ForeignKey(
        Topping,
        verbose_name='топпинг',
        on_delete=models.PROTECT,
        related_name='cakes'
    )
    berries = models.ForeignKey(
        Berry,
        verbose_name='ягоды',
        related_name='cakes',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    decorations = models.ForeignKey(
        Decoration,
        verbose_name='декор',
        related_name='cakes',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    text = models.CharField(
        verbose_name='надпись',
        max_length=75,
        blank=True
    )
    price = models.DecimalField(
        verbose_name='стоимость, руб.',
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        upload_to='cake/',
        null=True,
        blank=True,
        verbose_name="Изображение торта"
    )
    is_show = models.BooleanField(
        default=False,
        blank=True,
        null=True,
        verbose_name='отображение'
    )

    class Meta:
        verbose_name = 'торт'
        verbose_name_plural = 'торты'

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):

        total = (
                self.levels.price +
                self.form.price +
                self.topping.price
        )

        if self.berries:
            total += self.berries.price
        if self.decorations:
            total += self.decorations.price

        if self.text:
            total += 500

        self.price = total
        super().save(*args, **kwargs)


class Courier(models.Model):
    user = models.CharField(
        max_length=20,
        verbose_name='Курьер'
    )

    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон курьера'
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.00,
        validators=[MinValueValidator(0)],
        verbose_name='Рейтинг'
    )

    class Meta:
        verbose_name = 'курьер'
        verbose_name_plural = 'курьеры'

    def __str__(self):
        return f'Курьер {self.user}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('unprocessed', 'Необработанный'),
        ('underway', 'В работе'),
        ('delivery', 'Доставка'),
        ('completed', 'Завершен'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unprocessed',
        db_index=True,
        verbose_name='Статус'
    )
    user = models.ForeignKey(
        CustomUser,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    cake = models.ForeignKey(
        Cake,
        verbose_name='торт',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    courier = models.ForeignKey(
        Courier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='курьер',
        related_name='orders'
    )
    address = models.TextField(
        verbose_name='адрес',
        editable=True
    )
    order_notes = models.TextField(
        verbose_name='комментарий к заказу',
        blank=True
    )
    delivery_notes = models.TextField(
        verbose_name='комментарий для курьера',
        blank=True
    )
    delivery_date = models.DateField(
        verbose_name='дата доставки'
    )
    delivery_time = models.TimeField(
        verbose_name='время доставки'
    )
    cost = models.DecimalField(
        verbose_name='стоимость заказа',
        validators=[MinValueValidator(0)],
        decimal_places=2,
        max_digits=7
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.cake} - {self.address}'

    def save(self, *args, **kwargs):

        if not self.cost and self.cake:
            self.cost = self.cake.price

        if self.delivery_date and self.delivery_time:
            delivery_dt = datetime.combine(
                self.delivery_date,
                self.delivery_time
            )
            if timezone.is_naive(delivery_dt):
                delivery_dt = timezone.make_aware(
                    delivery_dt,
                    timezone.get_current_timezone()
                )

            delta = delivery_dt - timezone.now()
            if timedelta(0) < delta <= timedelta(hours=24):
                self.cost = (self.cost or Decimal('0')) * Decimal('1.2')

        super().save(*args, **kwargs)


class ClickCounter(models.Model):
    token = models.CharField(
        max_length=20,
        unique=True,
        default=get_random_string(length=20)
    )
    clicks = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.id}: {self.clicks} clicks'

    class Meta:
        verbose_name = 'реферальную ссылку'
        verbose_name_plural = 'реферальные ссылки'