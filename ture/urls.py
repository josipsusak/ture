from django.urls import path
from . import views

urlpatterns = [
    path('unos_ture/', views.home, name='unos_ture'),
    path('vozaci/', views.unos_vozaca, name='unos_vozaca'),
    path('vozac/<int:vozac_id>/', views.profil_vozaca, name='profil_vozaca'),
]
