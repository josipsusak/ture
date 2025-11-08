from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Tura, Vozac, Vozilo, Naputak
from .forms import TuraForm, VozacForm, VozacUpdateForm, VoziloForm, NaputakForm


def homepage(request):
    mjesec = request.GET.get('mjesec')
    godina = request.GET.get('godina')

    if mjesec and godina:
        ture = Tura.objects.filter(
            aktivan=True,
            datum_polaska__month=int(mjesec),
            datum_polaska__year=int(godina)
        ).order_by('datum_polaska')
    else:
        ture = Tura.objects.filter(aktivan=True).order_by('datum_polaska')

    # Ukupne vrijednosti
    total_km = ture.aggregate(Sum('kilometraza'))['kilometraza__sum'] or 0
    total_zaduz = ture.aggregate(Sum('zaduzenje'))['zaduzenje__sum'] or 0
    total_razduz = ture.aggregate(Sum('razduzenje'))['razduzenje__sum'] or 0
    total_razlika = ture.aggregate(Sum('razlika'))['razlika__sum'] or 0
    total_iznos = ture.aggregate(Sum('iznos_ture'))['iznos_ture__sum'] or 0
    total_dnevnice = ture.aggregate(Sum('dnevnice'))['dnevnice__sum'] or 0
    total_cekanje = ture.aggregate(Sum('cekanje'))['cekanje__sum'] or 0
    
    svi_mjeseci = range(1, 13)
    trenutna_godina = datetime.now().year
    
    vozila = Vozilo.objects.all()
    upozorenja = []
    for v in vozila:
        if v.registracija_blizu():
            upozorenja.append(f"⚠️ Vozilu {v.ime} ističe registracija {v.vrijeme_registracije.strftime('%d.%m.%Y')}.")
        if v.servis_blizu():
            upozorenja.append(f"🔧 Vozilo {v.ime} ima servis {v.servis.strftime('%d.%m.%Y')}.")

    return render(request, 'homepage.html', {
        'ture': ture,
        'total_km': total_km,
        'total_zaduz': total_zaduz,
        'total_razduz': total_razduz,
        'total_razlika': total_razlika,
        'total_iznos': total_iznos,
        'total_dnevnice': total_dnevnice,
        'total_cekanje': total_cekanje,
        'upozorenja': upozorenja,
        'svi_mjeseci': svi_mjeseci,
        'trenutna_godina': trenutna_godina,
        'odabrani_mjesec':int(mjesec) if mjesec else None,
        'odabrana_godina': int(godina) if godina else None,
    })

def unos_ture(request):
    if request.method == 'POST':
        form = TuraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('unos_ture')
    else:
        form = TuraForm()

    ture = Tura.objects.filter(aktivan=True).order_by('datum_polaska')

    # Ukupne vrijednosti
    total_km = ture.aggregate(Sum('kilometraza'))['kilometraza__sum'] or 0
    total_zaduz = ture.aggregate(Sum('zaduzenje'))['zaduzenje__sum'] or 0
    total_razduz = ture.aggregate(Sum('razduzenje'))['razduzenje__sum'] or 0
    total_razlika = ture.aggregate(Sum('razlika'))['razlika__sum'] or 0
    total_iznos = ture.aggregate(Sum('iznos_ture'))['iznos_ture__sum'] or 0
    total_dnevnice = ture.aggregate(Sum('dnevnice'))['dnevnice__sum'] or 0
    total_cekanje = ture.aggregate(Sum('cekanje'))['cekanje__sum'] or 0

    # Prenos u sljedeći mjesec 
    prenos = total_razlika - total_dnevnice - total_cekanje

    return render(request, 'unos_ture.html', {
        'form': form,
        'ture': ture,
        'total_km': total_km,
        'total_zaduz': total_zaduz,
        'total_razduz': total_razduz,
        'total_razlika': total_razlika,
        'total_iznos': total_iznos,
        'total_dnevnice': total_dnevnice,
        'total_cekanje': total_cekanje,
        'prenos': prenos,
    })

def unos_vozaca(request):
    if request.method == 'POST':
        form = VozacForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('popis_vozaca')
    else:
        form = VozacForm()

    vozac = Vozac.objects.all()
    return render(request, 'popis_vozaca.html', {'form': form, 'vozaci': vozac})

def profil_vozaca(request, vozac_id):
    vozac = get_object_or_404(Vozac, id=vozac_id)
    
    
    mjesec = request.GET.get('mjesec')
    godina = request.GET.get('godina')
    
    if mjesec and godina:
        ture = Tura.objects.filter(
            vozac=vozac,
            datum_dolaska__month=int(mjesec),
            datum_dolaska__year=int(godina)
            ).order_by('datum_polaska')
    else:
        ture = Tura.objects.filter(vozac=vozac).order_by('datum_polaska')
        
    if request.method == 'POST':
        form = VozacUpdateForm(request.POST, instance=vozac)
        if form.is_valid():
            form.save()
            for tura in ture:
                if tura.iznos_ture:
                    tura.dnevnice = round(tura.iznos_ture * vozac.postotak , 2)
                    tura.save(update_fields=['dnevnice'])
            return redirect('profil_vozaca', vozac_id=vozac.id) # type: ignore
    else:
        form = VozacUpdateForm(instance=vozac)

    # Izračun suma
    total_km = ture.aggregate(Sum('kilometraza'))['kilometraza__sum'] or 0
    total_zaduz = ture.aggregate(Sum('zaduzenje'))['zaduzenje__sum'] or 0
    total_razduz = ture.aggregate(Sum('razduzenje'))['razduzenje__sum'] or 0
    total_razlika = ture.aggregate(Sum('razlika'))['razlika__sum'] or 0
    total_iznos = ture.aggregate(Sum('iznos_ture'))['iznos_ture__sum'] or 0
    total_dnevnice = ture.aggregate(Sum('dnevnice'))['dnevnice__sum'] or 0
    total_cekanje = ture.aggregate(Sum('cekanje'))['cekanje__sum'] or 0

    # Prenos i bilanca
    bilanca = round(( total_razlika - total_dnevnice - total_cekanje + vozac.zaduzenje_prethodni_mjesec + vozac.uplaceno_na_banku),2)
    
    svi_mjeseci = range(1, 13)
    trenutna_godina = datetime.now().year

    return render(request, 'profil_vozaca.html', {
        'vozac': vozac,
        'ture': ture,
        'total_km': total_km,
        'total_zaduz': total_zaduz,
        'total_razduz': total_razduz,
        'total_razlika': total_razlika,
        'total_iznos': total_iznos,
        'total_dnevnice': total_dnevnice,
        'total_cekanje': total_cekanje,
        'bilanca': bilanca,
        'form': form,
        'svi_mjeseci': svi_mjeseci,
        'trenutna_godina': trenutna_godina,
        'odabrani_mjesec': int(mjesec) if mjesec else None,
        'odabrana_godina': int(godina) if godina else None,
    })
    
def dodavanje_vozaca(request):
    if request.method == 'POST':
        form = VozacForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('popis_vozaca')
    else:
        form = VozacForm()

    return render(request, 'dodavanje_vozaca.html', {'form': form})

def zavrsi_turu(request, tura_id):
    tura = get_object_or_404(Tura, id=tura_id)
    tura.aktivan = False
    tura.save()
    return redirect('unos_ture')  # Vrati korisnika na popis aktivnih tura

def profil_ture(request, tura_id):
    tura = get_object_or_404(Tura, id=tura_id)
    
    if request.method == 'POST':
        form = TuraForm(request.POST, instance=tura)
        if form.is_valid():
            form.save()
            return redirect('profil_ture', tura_id=tura.id) # type: ignore
    else:
        form = TuraForm(instance=tura)

    return render(request, 'profil_ture.html', {'tura': tura, 'form': form})

def popis_vozila(request):
    vozila = Vozilo.objects.all().order_by('ime')
    return render(request, 'vozila/popis_vozila.html', {'vozila': vozila})

def detalji_vozila(request, vozilo_id):
    vozilo = get_object_or_404(Vozilo, id=vozilo_id)
    naputci = vozilo.naputci.all().order_by('-datum') # type: ignore

    if request.method == 'POST':
        form = NaputakForm(request.POST)
        if form.is_valid():
            naputak = form.save(commit=False)
            naputak.vozilo = vozilo
            naputak.save()
            return redirect('detalji_vozila', vozilo_id=vozilo.id)# type: ignore
    else:
        form = NaputakForm()

    return render(request, 'vozila/detalji_vozila.html', {
        'vozilo': vozilo,
        'naputci': naputci,
        'form': form,
    })

def dodaj_vozilo(request):
    if request.method == 'POST':
        form = VoziloForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('popis_vozila')
    else:
        form = VoziloForm()
    return render(request, 'vozila/dodaj_vozilo.html', {'form': form})

def uredi_vozilo(request, vozilo_id):
    vozilo = get_object_or_404(Vozilo, id=vozilo_id)
    if request.method == 'POST':
        form = VoziloForm(request.POST, instance=vozilo)
        if form.is_valid():
            form.save()
            return redirect('detalji_vozila', vozilo_id=vozilo.id) # type: ignore
    else:
        form = VoziloForm(instance=vozilo)
    return render(request, 'vozila/uredi_vozilo.html', {'form': form, 'vozilo': vozilo})

def obrisi_vozilo(request, vozilo_id):
    vozilo = get_object_or_404(Vozilo, id=vozilo_id)
    if request.method == 'POST':
        vozilo.delete()
        return redirect('popis_vozila')
    return render(request, 'vozila/obrisi_vozilo.html', {'vozilo': vozilo})

def uredi_naputak(request, naputak_id):
    naputak = get_object_or_404(Naputak, id=naputak_id)
    vozilo = naputak.vozilo

    if request.method == 'POST':
        form = NaputakForm(request.POST, instance=naputak)
        if form.is_valid():
            form.save()
            return redirect('detalji_vozila', vozilo_id=vozilo.id)
    else:
        form = NaputakForm(instance=naputak)

    return render(request, 'uredi_naputak.html', {'form': form, 'naputak': naputak, 'vozilo': vozilo})


def obrisi_naputak(request, naputak_id):
    naputak = get_object_or_404(Naputak, id=naputak_id)
    vozilo = naputak.vozilo

    if request.method == 'POST':
        naputak.delete()
        return redirect('detalji_vozila', vozilo_id=vozilo.id)# type: ignore

    return render(request, 'obrisi_naputak.html', {'naputak': naputak, 'vozilo': vozilo})
