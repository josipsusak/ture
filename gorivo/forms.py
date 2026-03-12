from django import forms
from .models import TransakcijaGoriva, Tank

class PotrosnjaForm(forms.ModelForm):
    class Meta:
        model = TransakcijaGoriva
        fields = ["kolicina",'vozilo', "napomena"]
        
        labels = {
            "kolicina": "Količina (L)",
            "vozilo": "Vozilo",
            "napomena": "Napomena",
        }
    
        widgets = {
            "vozilo": forms.Select(attrs={"class": "form-control"}),
            "kolicina": forms.NumberInput(attrs={"class": "form-control"}),
            "napomena": forms.TextInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.tip = "potrosnja"
        if commit:
            obj.save()
        return obj


class RefillForm(forms.ModelForm):
    bih_gorivo = forms.FloatField(min_value=0, label="IH Transport (L)")
    rh_gorivo = forms.FloatField(min_value=0, label="Hrkać logistika (L)")

    class Meta:
        model = Tank
        fields = ["kapacitet"]
        
        labels = {
            "kapacitet": "Kapacitet tanka (L)",
        }

    def __init__(self, *args, **kwargs):
        tank = kwargs.pop("tank", None)
        super().__init__(*args, **kwargs)
        if tank:
            self.fields["bih_gorivo"].initial = 0
            self.fields["rh_gorivo"].initial = 0
            self.fields["kapacitet"].initial = tank.kapacitet
    
class RaspodjelaForm(forms.ModelForm):
    bih_gorivo = forms.FloatField(min_value=0, label="Gorivo za IH Transport")
    rh_gorivo = forms.FloatField(min_value=0, label="Gorivo za Hrkać logistika")

    class Meta:
        model = Tank
        fields = ["kapacitet"]
        
        labels = {
            "kapacitet": "Ukupni kapacitet tanka (L)",
        }

    def __init__(self, *args, **kwargs):
        tank = kwargs.pop("tank", None)
        super().__init__(*args, **kwargs)
        if tank:
            self.fields["bih_gorivo"].initial = tank.stanje_bih
            self.fields["rh_gorivo"].initial = tank.stanje_rh
            self.fields["kapacitet"].initial = tank.kapacitet

    def clean(self):
        cleaned = super().clean()
        ukupno = cleaned.get("kapacitet")
        bih = cleaned.get("bih_gorivo")
        rh = cleaned.get("rh_gorivo")

        if bih + rh > ukupno:
            raise forms.ValidationError(
                "Zbroj IH Transport i Hrkać logistika goriva ne može biti veći od ukupnog kapaciteta tanka!"
            )
        return cleaned