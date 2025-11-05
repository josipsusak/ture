from django.urls import path
from . import views

urlpatterns = [
    path('unos_ture', views.home, name='unos_ture'),
]
