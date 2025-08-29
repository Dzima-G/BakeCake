from django.shortcuts import render
from .models import Cake, Order


def index(request):
    cakes = Cake.objects.filter(is_show=True).order_by('id')[:3]

    return render(
        request,
        'index.html',
        {
            'cakes': cakes,
        })


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
