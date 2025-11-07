from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('unos_ture/', views.home, name='unos_ture'),
    path('vozaci/', views.unos_vozaca, name='popis_vozaca'),
    path('vozac/<int:vozac_id>/', views.profil_vozaca, name='profil_vozaca'),
    path('dodavanje_vozaca/', views.dodavanje_vozaca, name='dodavanje_vozaca'), 
    path('zavrsi_turu/<int:tura_id>/', views.zavrsi_turu, name='zavrsi_turu'), 
]
