from django.contrib import admin
from .models import Tura, Vozac

@admin.register(Tura)

class TuraAdmin(admin.ModelAdmin):
    list_display = ('relacija', 'datum_polaska', 'datum_dolaska', 'kilometraza', 'iznos_ture')
    search_fields = ('relacija', 'broj_putnog_naloga')
    list_filter = ('datum_polaska', 'datum_dolaska')
    
@admin.register(Vozac)
class VozacAdmin(admin.ModelAdmin):
    list_display = ('ime', 'zaduzenje_prethodni_mjesec', 'uplaceno_na_banku')
    search_fields = ('ime',)