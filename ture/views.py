from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Tura
from .forms import TuraForm

def home(request):
    if request.method == 'POST':
        form = TuraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('unos_ture')
    else:
        form = TuraForm()

    ture = Tura.objects.all().order_by('datum_polaska')

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

