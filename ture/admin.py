from django.contrib import admin
from .models import Tura

@admin.register(Tura)
class TuraAdmin(admin.ModelAdmin):
    list_display = ('relacija', 'datum_polaska', 'datum_dolaska', 'kilometraza', 'iznos_ture')
    search_fields = ('relacija', 'broj_putnog_naloga')
    list_filter = ('datum_polaska', 'datum_dolaska')
