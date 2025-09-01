from datetime import datetime, timedelta

from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from users.forms import LoginForm, SignupForm

from .forms import CakeForm
from .models import (Berry, Cake, CustomUser, Decoration, Form, Level, Order,
                     Topping, PromoCode)


def lk_user(request):
    orders = (
        Order.objects.filter(user=request.user)
    )
    for order in orders:
        order.berries_label = order.cake.berries.name if order.cake.berries else 'Без ягод'
        order.decorations_label = order.cake.decorations.name if order.cake.decorations else 'Без декора'
        order.text_label = (order.cake.text or '').strip() or 'Без надписи'
    context = {
        'orders': orders,
        'has_orders': orders.exists()
    }
    return render(
        request,
        'lk.html',
        context
    )


def catalog(request):
    cakes = Cake.objects.filter(is_show=True)
    for cake in cakes:
        cake.berries_label = cake.berries.name if cake.berries else 'Без ягод'
        cake.decorations_label = cake.decorations.name if cake.decorations else 'Без декора'
        cake.text_label = (cake.text or '').strip() or 'Без надписи'

    return render(
        request,
        'catalog.html',
        {
            'cakes': cakes,
        })


def index(request):
    cakes = Cake.objects.filter(is_show=True).order_by('id')[:3]
    order = None
    signup_form = SignupForm()
    login_form = LoginForm()

    if request.method == 'POST':
        form = CakeForm(request.POST)
        if form.is_valid():
            cake = form.save()
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                cake=cake,
                address=request.POST.get('address', ''),
                order_notes=request.POST.get('order_notes', ''),
                delivery_notes=request.POST.get('delivery_notes', ''),
                delivery_date=request.POST.get('delivery_date'),
                delivery_time=request.POST.get('delivery_time'),
                cost=cake.price
            )
            form = CakeForm()
    else:
        form = CakeForm()

    min_delivery_time = 15
    min_dt = timezone.now() + timedelta(hours=min_delivery_time)

    context = {
        'form': form,
        'levels': Level.objects.all(),
        'forms': Form.objects.all(),
        'toppings': Topping.objects.all(),
        'berries': Berry.objects.all(),
        'decorations': Decoration.objects.all(),
        'order': order,
        'signup_form': signup_form,
        'login_form': login_form,
        'cakes': cakes,
        'min_date': min_dt.date(),
        'min_time': min_dt.strftime('%H:%M'),
        'text_price': 500,
    }
    return render(
        request,
        'index.html',
        context
    )


def create_order(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': 'Неверный метод'}, status=405)

    # Собираем торт
    cake_form = CakeForm(request.POST)
    if not cake_form.is_valid():
        return JsonResponse({'ok': False, 'message': 'Ошибка в данных торта', 'errors': cake_form.errors}, status=400)
    cake = cake_form.save()

    # Если пользователь не авторизован — регистрируем его
    if not request.user.is_authenticated:
        signup_form = SignupForm(request.POST)
        if not signup_form.is_valid():
            return JsonResponse({'ok': False, 'message': 'Ошибка регистрации', 'errors': signup_form.errors},
                                status=400)
        user = CustomUser.objects.create_user(
            phone=signup_form.cleaned_data['phone'],
            first_name=signup_form.cleaned_data.get('first_name', ''),
            email=signup_form.cleaned_data.get('email', ''),
            password=signup_form.cleaned_data['password1'],
        )
        login(request, user)
    else:
        user = request.user

    delivery_date_str = request.POST.get('delivery_date')
    delivery_time_str = request.POST.get('delivery_time')
    delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date() if delivery_date_str else None
    delivery_time = datetime.strptime(delivery_time_str, '%H:%M').time() if delivery_time_str else None

    # валидация даты доставки
    min_delivery_time = 15
    if delivery_date and delivery_time:
        selected_dt = datetime.combine(delivery_date, delivery_time)
        selected_dt = timezone.make_aware(selected_dt, timezone.get_current_timezone())

        min_allowed = timezone.now() + timedelta(hours=min_delivery_time)

        if selected_dt < min_allowed:
            return JsonResponse(
                {'ok': False, 'message': 'Доставка возможна не ранее чем через 15 часов'},
                status=400
            )

    raw_code = (request.POST.get('promo') or '').strip()
    promo = None
    if raw_code:
        promo = PromoCode.objects.filter(code__iexact=raw_code).first()

    # Создаём заказ
    order = Order.objects.create(
        user=user,
        cake=cake,
        address=request.POST.get('address', ''),
        order_notes=request.POST.get('order_notes', ''),
        delivery_notes=request.POST.get('delivery_notes', ''),
        delivery_date=delivery_date,
        delivery_time=delivery_time,
        cost=cake.price,
        promo=promo,
    )
    return JsonResponse({
        'ok': True,
        'message': f"Заказ №{order.id} создан успешно!",
        'redirect_url': reverse('storage:lk_user'),
    })


def create_order_catalog(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': 'Неверный метод'}, status=405)

    # Если пользователь не авторизован — регистрируем его
    if not request.user.is_authenticated:
        signup_form = SignupForm(request.POST)
        if not signup_form.is_valid():
            return JsonResponse({'ok': False, 'message': 'Ошибка регистрации', 'errors': signup_form.errors},
                                status=400)
        user = CustomUser.objects.create_user(
            phone=signup_form.cleaned_data['phone'],
            first_name=signup_form.cleaned_data.get('first_name', ''),
            email=signup_form.cleaned_data.get('email', ''),
            password=signup_form.cleaned_data['password1'],
        )
        login(request, user)
    else:
        user = request.user

    # Получаем оригинальный торт из каталога по ID
    cake_id = request.POST.get('cake_id')
    try:
        original_cake = Cake.objects.get(id=cake_id)
    except Cake.DoesNotExist:
        return JsonResponse({'ok': False, 'message': 'Торт не найден'}, status=400)

    # Создаем кастомную копию торта
    text = request.POST.get('text', '').strip()
    final_price = original_cake.price

    if text:
        custom_cake = Cake.objects.create(
            levels=original_cake.levels,
            form=original_cake.form,
            topping=original_cake.topping,
            berries=original_cake.berries,
            decorations=original_cake.decorations,
            text=text,
            price=original_cake.price + 500,
            name=f"{original_cake.name} (Кастом)"
        )
        final_cake = custom_cake
        final_price = custom_cake.price
    else:
        final_cake = original_cake
        final_price = original_cake.price

    # Обработка даты и времени
    delivery_date_str = request.POST.get('delivery_date')
    delivery_time_str = request.POST.get('delivery_time')

    delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date() if delivery_date_str else None
    delivery_time = datetime.strptime(delivery_time_str, '%H:%M').time() if delivery_time_str else None

    raw_code = (request.POST.get('promo') or '').strip()
    promo = None
    if raw_code:
        promo = PromoCode.objects.filter(code__iexact=raw_code).first()

    # Создаём заказ
    order = Order.objects.create(
        user=user,
        cake=final_cake,
        address=request.POST.get('address', ''),
        order_notes=request.POST.get('order_notes', ''),
        delivery_notes=request.POST.get('delivery_notes', ''),
        delivery_date=delivery_date,
        delivery_time=delivery_time,
        cost=final_price,
        promo=promo,
    )

    return redirect('storage:lk_user')
