from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Tura, Vozac
from .forms import TuraForm, VozacForm, VozacUpdateForm

def homepage(request):

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

    return render(request, 'homepage.html', {
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

def home(request):
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

    return render(request, 'home.html', {
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
