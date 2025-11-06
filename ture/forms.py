from django import forms
from .models import Tura, Vozac

class VozacForm(forms.ModelForm):
    class Meta:
        model = Vozac
        fields = ['ime','zaduzenje_prethodni_mjesec', 'uplaceno_na_banku', 'postotak']
        labels = {
            'ime': 'Ime vozača',
            'zaduzenje_prethodni_mjesec': 'Zaduženje za prošli mjesec',
            'uplaceno_na_banku': 'Uplaćeno na banku za prošli mjesec',
            'postotak': 'Postotak vozača',
        }

class TuraForm(forms.ModelForm):
    class Meta:
        model = Tura
        fields = [
            'vozac',
            'relacija',
            'datum_polaska',
            'datum_dolaska',
            'kilometraza',
            'zaduzenje',
            'razduzenje',
            'broj_putnog_naloga',
            'iznos_ture',
            'cekanje',
        ]
        widgets = {
            'datum_polaska': forms.DateInput(attrs={'type': 'date'}),
            'datum_dolaska': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'vozac': 'Vozač',
            'relacija': 'Relacija',
            'datum_polaska': 'Datum polaska',
            'datum_dolaska': 'Datum dolaska',
            'kilometraza': 'Kilometraža',
            'zaduzenje': 'Zaduženje',
            'razduzenje':'Razduženje',
            'broj_putnog_naloga': 'Broj putnog naloga',
            'iznos_ture': 'Iznos ture',
            'cekanje': 'Čekanje',
        }
        
class VozacUpdateForm(forms.ModelForm):
    class Meta:
        model = Vozac
        fields = ['zaduzenje_prethodni_mjesec', 'uplaceno_na_banku', 'postotak']
        labels = {
            'zaduzenje_prethodni_mjesec': 'Zaduženje za prošli mjesec',
            'uplaceno_na_banku': 'Uplaćeno na banku za prošli mjesec',
            'postotak': 'Postotak vozača',
        }
