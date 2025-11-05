from django.db import models

class Tura(models.Model):
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

    def save(self, *args, **kwargs):
        # Razlika = Zaduženje - Razduženje
        if self.zaduzenje is not None and self.razduzenje is not None:
            self.razlika = self.zaduzenje - self.razduzenje
        
        # Dnevnice = (iznos_ture*1.16) - iznos_ture = iznos_ture * 0.16
        if self.iznos_ture is not None:
            self.dnevnice = round(self.iznos_ture * 0.16, 2)

        super().save(*args, **kwargs)
