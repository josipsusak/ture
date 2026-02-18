from django import forms
from .models import Tura, Vozac, Vozilo, Naputak, RadniNalog

class VozacForm(forms.ModelForm):
    class Meta:
        model = Vozac
        fields = ['ime','zaduzenje_prethodni_mjesec', 'uplaceno_na_banku', 'postotak', 'valuta']
        labels = {
            'ime': 'Ime vozača',
            'zaduzenje_prethodni_mjesec': 'Zaduženje za prošli mjesec',
            'uplaceno_na_banku': 'Uplaćeno na banku za prošli mjesec',
            'postotak': 'Postotak vozača',
            'valuta': 'Valuta vozača',
        }

class TuraForm(forms.ModelForm):
    class Meta:
        model = Tura
        fields = [
            'vozac',
            'relacija',
            'datum_polaska',
            'datum_dolaska',
            'granica_polazak',
            'granica_povratak',
            'kilometraza',
            'zaduzenje',
            'razduzenje',
            'broj_putnog_naloga',
            'iznos_ture',
            'cekanje',
            'aktivan',
        ]
        widgets = {
            'datum_polaska': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'datum_dolaska': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'granica_polazak': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'granica_povratak': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'relacija': forms.Textarea(attrs={'rows': 2, 'cols': 80}),
        }
        labels = {
            'vozac': 'Vozač',
            'relacija': 'Relacija',
            'datum_polaska': 'Datum polaska',
            'datum_dolaska': 'Datum dolaska',
            'granica_polazak': 'Prelazak granice - polazak',
            'granica_povratak': 'Prelazak granice - povratak',
            'kilometraza': 'Kilometraža',
            'zaduzenje': 'Zaduženje',
            'razduzenje':'Razduženje',
            'broj_putnog_naloga': 'Broj putnog naloga',
            'iznos_ture': 'Iznos ture',
            'cekanje': 'Čekanje',
            'aktivan': 'Aktivan',
        }
        
class VozacUpdateForm(forms.ModelForm):
    class Meta:
        model = Vozac
        fields = ['zaduzenje_prethodni_mjesec', 'uplaceno_na_banku', 'postotak', 'valuta']
        labels = {
            'zaduzenje_prethodni_mjesec': 'Zaduženje za prošli mjesec',
            'uplaceno_na_banku': 'Uplaćeno na banku za prošli mjesec',
            'postotak': 'Postotak vozača',
            'valuta': 'Valuta vozača',
        }
        
class VoziloForm(forms.ModelForm):
    class Meta:
        model = Vozilo
        fields = ['vozac', 'ime', 'vrijeme_registracije', 'servis', 'periodicni_pregled', 'bazdar_tahografa', 'pozarni_aparati', 'tu_potvrda']
        widgets = {
            'vrijeme_registracije': forms.DateInput(attrs={'type': 'date'}),
            'servis': forms.DateInput(attrs={'type': 'date'}),
            'periodicni_pregled': forms.DateInput(attrs={'type': 'date'}),
            'bazdar_tahografa': forms.DateInput(attrs={'type': 'date'}),
            'pozarni_aparati': forms.DateInput(attrs={'type': 'date'}),
            'tu_potvrda': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'vozac': 'Vozač',
            'ime': 'Ime vozila',
            'vrijeme_registracije': 'Vrijeme registracije',
            'servis': 'Servis',
            'periodicni_pregled': 'Periodični pregled',
            'bazdar_tahografa': 'Baždarenje tahografa',
            'pozarni_aparati': 'Požarni aparati',
            'tu_potvrda': 'TU potvrda',
        }
 

class NaputakForm(forms.ModelForm):
    class Meta:
        model = Naputak
        fields = ['sadrzaj']
        widgets = {
            'sadrzaj': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Upiši naputak...'})
        }
        labels = {
            'sadrzaj': 'Sadržaj naputka',
        }
        

class RadniNalogForm(forms.ModelForm):
    class Meta:
        model = RadniNalog
        fields = ['tura', 'konacna_drzava', 'papiri', 'terminali', 'cestarine', 'ostali_troskovi', 'izdaci', 'aktivan']
        labels = {
            'tura': 'Tura',
            'konacna_drzava': 'Konačna država',
            'papiri': 'Papiri',
            'terminali': 'Terminali',
            'cestarine': 'Cestarine',
            'ostali_troskovi': 'Ostali troškovi',
            'izdaci': 'Izdaci',
            'aktivan': 'Aktivan',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tura'].queryset = Tura.objects.filter(aktivan=True)

        