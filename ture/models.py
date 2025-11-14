from django.db import models
from datetime import date
from django.forms import ValidationError

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
    datum_polaska = models.DateTimeField()
    datum_dolaska = models.DateTimeField(blank=True, null=True)
    kilometraza = models.FloatField(blank=True, null=True)
    zaduzenje = models.FloatField()
    razduzenje = models.FloatField(blank=True, null=True)
    razlika = models.FloatField(blank=True, null=True)
    broj_putnog_naloga = models.CharField(max_length=50, blank=True, null=True)
    iznos_ture = models.FloatField(blank=True, null=True)
    dnevnice = models.FloatField(blank=True, null=True) 
    cekanje = models.FloatField(blank=True, null=True) 
    aktivan = models.BooleanField(default=True)  
    granica_polazak = models.DateTimeField(blank=True, null=True)
    granica_povratak = models.DateTimeField(blank=True, null=True)
    
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
    
class RadniNalog(models.Model):
    tura = models.OneToOneField(Tura, on_delete=models.CASCADE, related_name='radni_nalog')
    konacna_drzava = models.CharField(max_length=50, choices=[
        ('BiH','BiH'), ('Austrija','Austrija'), ('Njemacka','Njemacka'),
        ('Slovenija','Slovenija'), ('Francuska','Francuska'), ('Hrvatska','Hrvatska'),
        ('Madjarska','Madjarska'), ('Svicarska','Svicarska'), ('Italija','Italija')
    ])
    tuzemne_dnevnice = models.FloatField(blank=True, null=True)
    inozemne_dnevnice = models.FloatField(blank=True, null=True)
    
    def clean(self):
        """
        Validacija granica.
        """
        if self.tura:
            gp = self.tura.granica_polazak
            gv = self.tura.granica_povratak

            if gp and gv:
                if gv < gp:
                    raise ValidationError("Vrijeme povratka preko granice ne može biti prije polaska preko granice.")

    def izracun_dnevnica(self):
        t = self.tura

        # Cijene po državama
        cijene = {
            'BiH': 12.5,
            'Austrija': 90,
            'Njemacka': 90,
            'Slovenija': 80,
            'Francuska': 90,
            'Hrvatska': 50,
            'Madjarska': 70,
            'Svicarska': 90,
            'Italija': 80,
        }

        if not t or not t.datum_polaska or not t.datum_dolaska:
            self.tuzemne_dnevnice = 0
            self.inozemne_dnevnice = 0
            return

        # Pretvorba sati -> broj dnevnica prema pravilima
        def u_dnevnica(sati):
            if sati <= 0:
                return 0.0
            if sati <= 8:
                return 0.5
            if sati <= 24:
                return 1.0
            puni = int(sati // 24)
            ostatak = sati % 24
            dodatno = 0.5 if ostatak <= 8 else 1.0
            return puni + dodatno

        # 1) ukupno (za cijelu turu)
        ukupni_sati = (t.datum_dolaska - t.datum_polaska).total_seconds() / 3600.0
        ukupno_dnevnice = u_dnevnica(ukupni_sati)

        # 2) ako je konačna država BiH -> sve tuzemno
        if self.konacna_drzava == "BiH":
            self.inozemne_dnevnice = 0.0
            self.tuzemne_dnevnice = round(ukupno_dnevnice * cijene['BiH'], 2)
            return

        # 3) ako nema granica -> sve tuzemno
        if not t.granica_polazak or not t.granica_povratak:
            self.inozemne_dnevnice = 0.0
            self.tuzemne_dnevnice = round(ukupno_dnevnice * cijene['BiH'], 2)
            return

        # 4) inozemne (interval između granica)
        inozem_sati = (t.granica_povratak - t.granica_polazak).total_seconds() / 3600.0
        inozemne_dnev = u_dnevnica(inozem_sati)

        # 5) tuzemne (prije granice + poslije granice)
        tuzem_sati = 0.0
        if t.datum_polaska < t.granica_polazak:
            tuzem_sati += (t.granica_polazak - t.datum_polaska).total_seconds() / 3600.0
        if t.datum_dolaska > t.granica_povratak:
            tuzem_sati += (t.datum_dolaska - t.granica_povratak).total_seconds() / 3600.0
        tuzemne_dnev = u_dnevnica(tuzem_sati)

        # 6) IMEDIATNI CAP: ako zbroj prelazi ukupno_dnevnice -> smanji samo inozemne
        suma = inozemne_dnev + tuzemne_dnev
        if suma > ukupno_dnevnice:
            # smanjimo inozemne tolik da suma == ukupno_dnevnice
            inozemne_dnev = max(0.0, ukupno_dnevnice - tuzemne_dnev)

        # 7) konačan izračun u eurima
        cij_ino = cijene.get(self.konacna_drzava, 50)
        cij_tuz = cijene['BiH']

        self.inozemne_dnevnice = round(inozemne_dnev * cij_ino, 2)
        self.tuzemne_dnevnice = round(tuzemne_dnev * cij_tuz, 2)


    def save(self, *args, **kwargs):
        self.izracun_dnevnica()
        super().save(*args, **kwargs)

def osvjezi_radni_nalog(tura):
    try:
        rn = RadniNalog.objects.get(tura=tura)
    except RadniNalog.DoesNotExist:
        return  # ako nema radnog naloga, nema šta osvježavati

    rn.vozac = tura.vozac #type: ignore
    rn.relacija = tura.relacija #type: ignore
    rn.vrijeme_polaska = tura.datum_polaska #type: ignore
    rn.vrijeme_povratka = tura.datum_dolaska #type: ignore
    rn.vrijeme_granica_polazak = tura.granica_polazak #type: ignore
    rn.vrijeme_granica_povratak = tura.granica_povratak #type: ignore

    rn.save()    