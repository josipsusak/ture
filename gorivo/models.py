from django.db import models
from django.core.exceptions import ValidationError
from ture.models import Vozilo

class Tank(models.Model):
    kapacitet = models.FloatField(default=5000)

    @property
    def stanje_bih(self):
        refill = self.transakcije.filter(drzava="bih", tip="refill").aggregate(sum=models.Sum('kolicina'))['sum'] or 0
        potrosnja = self.transakcije.filter(drzava="bih", tip="potrosnja").aggregate(sum=models.Sum('kolicina'))['sum'] or 0
        ukupno_stanje_bih = refill - potrosnja
        return ukupno_stanje_bih 

    @property
    def stanje_rh(self):
        refill = self.transakcije.filter(drzava="rh", tip="refill").aggregate(sum=models.Sum('kolicina'))['sum'] or 0
        potrosnja = self.transakcije.filter(drzava="rh", tip="potrosnja").aggregate(sum=models.Sum('kolicina'))['sum'] or 0
        ukupno_stanje_rh = refill - potrosnja
        return ukupno_stanje_rh

    @property
    def ukupno_stanje(self):
        ukupno_stanje = self.stanje_bih + self.stanje_rh if self.stanje_bih + self.stanje_rh <= self.kapacitet else self.kapacitet
        return ukupno_stanje

    @property
    
    def upozorenje_prazan_tank(self):
        return self.ukupno_stanje < 500


class TransakcijaGoriva(models.Model):

    TIPOVI = [
        ("refill", "Punjenje"),
        ("potrosnja", "Potrošnja"),
    ]

    DRZAVE = [
        ("bih", "BiH"),
        ("rh", "RH"),
    ]

    tank = models.ForeignKey(Tank, related_name="transakcije", on_delete=models.CASCADE)
    tip = models.CharField(max_length=20, choices=TIPOVI)
    drzava = models.CharField(max_length=3, choices=DRZAVE, null=True, blank=True)
    kolicina = models.FloatField()
    datum = models.DateTimeField(auto_now_add=True)
    napomena = models.TextField(blank=True, null=True)
    vozilo = models.ForeignKey(Vozilo,on_delete=models.SET_NULL,null=True,blank=True,related_name="tocenja")

    def __str__(self):
        return f"{self.tip} {self.kolicina} L ({self.drzava})"

    def clean(self):
        if self.tip == "potrosnja" and not self.vozilo:
            raise ValidationError("Kod potrošnje mora biti odabrano vozilo.")
        
        if self.tip == "refill":
            trenutno = self.tank.ukupno_stanje

            if trenutno + self.kolicina > self.tank.kapacitet:
                raise ValidationError(
                    f"Tank nema dovoljno kapaciteta. Preostalo mjesta: {self.tank.kapacitet - trenutno} L"
                )

    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)