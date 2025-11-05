from django import forms
from .models import Tura

class TuraForm(forms.ModelForm):
    class Meta:
        model = Tura
        fields = [
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
