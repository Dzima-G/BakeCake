from django.urls import path

from . import views

app_name = 'storage'

urlpatterns = [
    path('', views.index, name='index'),
    path('create-order/', views.create_order, name='create_order'),
    path('create-order-catalog/', views.create_order_catalog, name='create_order_catalog'),
    path('lk_user/', views.lk_user, name='lk_user'),
    path('catalog/', views.catalog, name='catalog'),
]