from django.urls import path

from . import views

app_name = 'storage'

urlpatterns = [
    path('', views.index, name='index'),
    path("lk_user/", views.lk_user, name='lk_user'),
    path("catalog/", views.catalog, name='catalog'),
]