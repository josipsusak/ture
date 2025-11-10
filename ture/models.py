from django.db import models
from datetime import date

class Vozac(models.Model):
    ime = models.CharField(max_length=100)
    zaduzenje_prethodni_mjesec = models.FloatField(default=0)
    uplaceno_na_banku = models.FloatField(default=0)
    postotak = models.FloatField(default=0)

    def __str__(self):
        return self.ime

class Tura(models.Model):
    vozac = models.ForeignKey(Vozac, on_delete=models.CASCADE, related_name='ture')
    relacija = models.CharField(max_length=255)
    datum_polaska = models.DateField()
    datum_dolaska = models.DateField()
    kilometraza = models.FloatField()
    zaduzenje = models.FloatField()
    razduzenje = models.FloatField()
    razlika = models.FloatField(blank=True, null=True)
    broj_putnog_naloga = models.CharField(max_length=50, blank=True, null=True)
    iznos_ture = models.FloatField()
    dnevnice = models.FloatField(blank=True, null=True) 
    cekanje = models.FloatField(blank=True, null=True) 
    aktivan = models.BooleanField(default=True)  
    
    def __str__(self):
        return f"{self.vozac.ime} - {self.relacija}"

    def save(self, *args, **kwargs):
        # Razlika = Zaduženje - Razduženje
        if self.zaduzenje is not None and self.razduzenje is not None:
            self.razlika = self.zaduzenje - self.razduzenje
        
        # Dnevnice = (iznos_ture*1.16) - iznos_ture = iznos_ture * 0.16
        if self.iznos_ture is not None and self.vozac and self.vozac.postotak:
            self.dnevnice = round(self.iznos_ture * self.vozac.postotak, 2)

        super().save(*args, **kwargs)
        
class Vozilo(models.Model):
    vozac = models.ForeignKey(Vozac, on_delete=models.SET_NULL, null=True, blank=True, related_name='vozila')
    ime = models.CharField(max_length=100)
    vrijeme_registracije = models.DateField()
    servis = models.DateField()
    dodatne_informacije = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.ime} ({self.vozac.ime if self.vozac else 'bez vozača'})"
    
    def registracija_blizu(self):
        return 0 <= (self.vrijeme_registracije - date.today()).days <= 14

    def servis_blizu(self):
        return 0 <= (self.servis - date.today()).days <= 14
    
    def registracija_istekla(self):
        return self.vrijeme_registracije < date.today()

    def servis_istekao(self):
        return self.servis < date.today()

class Naputak(models.Model):
    vozilo = models.ForeignKey('Vozilo', on_delete=models.CASCADE, related_name='naputci')
    sadrzaj = models.TextField("Sadržaj naputka")
    datum = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-datum']

    def __str__(self):
        return f"Naputak za {self.vozilo.ime} ({self.datum.strftime('%d.%m.%Y %H:%M')})"
    