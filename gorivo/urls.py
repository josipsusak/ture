from django.urls import path
from . import views

urlpatterns = [
    path("", views.gorivo_view, name="gorivo"),
    path("potrosnja/", views.dodaj_potrosnju, name="dodaj_potrosnju"),
    path("refill/", views.dodaj_refill, name="dodaj_refill"),
    path("raspodjela/", views.raspodjela_view, name="raspodjela"),
]