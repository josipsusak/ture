from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('unos_ture/', views.unos_ture, name='unos_ture'),
    path('vozaci/', views.unos_vozaca, name='popis_vozaca'),
    path('vozac/<int:vozac_id>/', views.profil_vozaca, name='profil_vozaca'),
    path('dodavanje_vozaca/', views.dodavanje_vozaca, name='dodavanje_vozaca'), 
    path('zavrsi_turu/<int:tura_id>/', views.zavrsi_turu, name='zavrsi_turu'), 
    path('profil_ture/<int:tura_id>/', views.profil_ture, name='profil_ture'),
    path('vozila/', views.popis_vozila, name='popis_vozila'),
    path('vozila/dodaj/', views.dodaj_vozilo, name='dodaj_vozilo'),
    path('vozila/<int:vozilo_id>/', views.detalji_vozila, name='detalji_vozila'),
    path('vozila/<int:vozilo_id>/uredi/', views.uredi_vozilo, name='uredi_vozilo'),
    path('vozila/<int:vozilo_id>/obrisi/', views.obrisi_vozilo, name='obrisi_vozilo'),
    path('naputak/<int:naputak_id>/uredi/', views.uredi_naputak, name='uredi_naputak'),
    path('naputak/<int:naputak_id>/obrisi/', views.obrisi_naputak, name='obrisi_naputak'),
    path('vozac/<int:vozac_id>/export-pdf/', views.export_vozac_pdf, name='export_vozac_pdf'),
]
