from django.db import models
from datetime import date
from django.forms import ValidationError

class Vozac(models.Model):
    
    VALUTA_CHOICES = [
        ('KM', 'KM'),
        ('EUR', 'EUR'),
    ]
    
    ime = models.CharField(max_length=100)
    zaduzenje_prethodni_mjesec = models.FloatField(default=0)
    uplaceno_na_banku = models.FloatField(default=0)
    postotak = models.FloatField(default=0)
    valuta = models.CharField(
        max_length=3,
        choices=VALUTA_CHOICES,
        default='KM'
    )

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
            self.dnevnice = round(self.iznos_ture * (self.vozac.postotak/100), 2)

        super().save(*args, **kwargs)
        
class Vozilo(models.Model):
    vozac = models.ForeignKey(Vozac, on_delete=models.SET_NULL, null=True, blank=True, related_name='vozila')
    ime = models.CharField(max_length=100)
    vrijeme_registracije = models.DateField()
    servis = models.DateField()
    periodicni_pregled = models.DateField(blank=True, null=True)
    bazdar_tahografa = models.DateField(blank=True, null=True)
    pozarni_aparati = models.DateField(blank=True, null=True)
    tu_potvrda = models.DateField(blank=True, null=True)
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
    
    def periodicni_pregled_blizu(self):
        if self.periodicni_pregled:
            return 0 <= (self.periodicni_pregled - date.today()).days <= 14
        return False

    def periodicni_pregled_istekao(self):
        return self.periodicni_pregled and self.periodicni_pregled < date.today()

    def bazdarenje_blizu(self):
        if self.bazdar_tahografa:
            return 0 <= (self.bazdar_tahografa - date.today()).days <= 14
        return False

    def bazdarenje_isteklo(self):
        return self.bazdar_tahografa and self.bazdar_tahografa < date.today()

    def pozarni_aparati_blizu(self):
        if self.pozarni_aparati:
            return 0 <= (self.pozarni_aparati - date.today()).days <= 14
        return False

    def pozarni_aparati_istekli(self):
        return self.pozarni_aparati and self.pozarni_aparati < date.today()

    def tu_potvrda_blizu(self):
        if self.tu_potvrda:
            return 0 <= (self.tu_potvrda - date.today()).days <= 14
        return False

    def tu_potvrda_istekla(self):
        return self.tu_potvrda and self.tu_potvrda < date.today()

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
        ('BiH','BiH'), ('Austrija','Austrija'), ('Njemačka','Njemačka'),
        ('Slovenija','Slovenija'), ('Francuska','Francuska'), ('Hrvatska','Hrvatska'),
        ('Mađarska','Mađarska'), ('Švicarska','Švicarska'), ('Italija','Italija')
    ])
    tuzemne_dnevnice = models.FloatField(blank=True, null=True)
    inozemne_dnevnice = models.FloatField(blank=True, null=True)
    aktivan = models.BooleanField(default=True)  
    papiri = models.FloatField(blank=True, null=True)
    terminali = models.FloatField(blank=True, null=True)
    cestarine = models.FloatField(blank=True, null=True)
    ostali_troskovi = models.TextField(blank=True, null=True)
    izdaci = models.TextField(blank=True, null=True)
    
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

        # --- 1. Dohvati cijene iz baze (CijenaDnevnica) ---
        cijene_dict = {c.drzava: c.iznos for c in CijenaDnevnica.objects.all()}
        
        # Fallback ako nema cijena u bazi (npr. prvo pokretanje)
        default_cijene = {
            'BiH': 12.5, 'Austrija': 90, 'Njemačka': 90, 'Slovenija': 80,
            'Francuska': 90, 'Hrvatska': 50, 'Mađarska': 70,
            'Švicarska': 90, 'Italija': 80,
        }
        cijene = {**default_cijene, **cijene_dict}  # baza ima prednost

        # --- 2. Validacija vremena ---
        if not t or not t.datum_polaska or not t.datum_dolaska:
            self.tuzemne_dnevnice = 0
            self.inozemne_dnevnice = 0
            return

        # --- 3. Pomoćna funkcija: sati → dnevnice ---
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

        # --- 4. Ukupno vrijeme ture ---
        ukupni_sati = (t.datum_dolaska - t.datum_polaska).total_seconds() / 3600.0
        ukupno_dnevnice = u_dnevnica(ukupni_sati)

        # --- 5. Ako je konačna država BiH → sve tuzemno ---
        if self.konacna_drzava == "BiH":
            self.inozemne_dnevnice = 0.0
            self.tuzemne_dnevnice = round(ukupno_dnevnice * cijene['BiH'], 2)
            return

        # --- 6. Ako nema granica → sve tuzemno ---
        if not t.granica_polazak or not t.granica_povratak:
            self.inozemne_dnevnice = 0.0
            self.tuzemne_dnevnice = round(ukupno_dnevnice * cijene['BiH'], 2)
            return

        # --- 7. Inozemne dnevnice (između granica) ---
        inozem_sati = (t.granica_povratak - t.granica_polazak).total_seconds() / 3600.0
        inozemne_dnev = u_dnevnica(inozem_sati)

        # --- 8. Tuzemne (prije + poslije granice) ---
        tuzem_sati = 0.0
        if t.datum_polaska < t.granica_polazak:
            tuzem_sati += (t.granica_polazak - t.datum_polaska).total_seconds() / 3600.0
        if t.datum_dolaska > t.granica_povratak:
            tuzem_sati += (t.datum_dolaska - t.granica_povratak).total_seconds() / 3600.0
        tuzemne_dnev = u_dnevnica(tuzem_sati)

        # --- 9. CAP: zbroj ne smije biti veći od ukupno_dnevnice ---
        suma = inozemne_dnev + tuzemne_dnev
        if suma > ukupno_dnevnice:
            inozemne_dnev = max(0.0, ukupno_dnevnice - tuzemne_dnev)

        # --- 10. Konačni izračun u EUR ---
        cij_ino = cijene.get(self.konacna_drzava, 50)
        cij_tuz = cijene.get('BiH', 12.5)

        if self.tura.vozac.valuta == 'EUR':
            self.inozemne_dnevnice = round(inozemne_dnev * cij_ino, 2)
            self.tuzemne_dnevnice = round(tuzemne_dnev * cij_tuz, 2)
        else:
            self.inozemne_dnevnice = round(inozemne_dnev * cij_ino , 2) #* 1.95583
            self.tuzemne_dnevnice = round(tuzemne_dnev * cij_tuz , 2) #* 1.95583


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
    
# models.py - dodaj na kraj
class CijenaDnevnica(models.Model):
    DRZAVE = [
        ('BiH', 'BiH'),
        ('Austrija', 'Austrija'),
        ('Njemacka', 'Njemačka'),
        ('Slovenija', 'Slovenija'),
        ('Francuska', 'Francuska'),
        ('Hrvatska', 'Hrvatska'),
        ('Madjarska', 'Mađarska'),
        ('Svicarska', 'Švicarska'),
        ('Italija', 'Italija'),
    ]

    drzava = models.CharField(max_length=50, choices=DRZAVE, unique=True)
    iznos = models.FloatField(help_text="Iznos dnevnica u EUR po danu")

    class Meta:
        verbose_name_plural = "Cijene dnevnica"

    def __str__(self):
        return f"{self.get_drzava_display()} - {self.iznos} €" #type: ignore