import os
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import A4, landscape # type: ignore
from reportlab.pdfbase import pdfmetrics# type: ignore
from reportlab.pdfbase.ttfonts import TTFont# type: ignore
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer# type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle# type: ignore
from reportlab.lib import colors# type: ignore
from .models import Tura, Vozac, Vozilo, Naputak, RadniNalog, osvjezi_radni_nalog
from .forms import TuraForm, VozacForm, VozacUpdateForm, VoziloForm, NaputakForm, RadniNalogForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('homepage') 

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, 'Neispravno korisničko ime ili lozinka.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def homepage(request):
    mjesec = request.GET.get('mjesec')
    godina = request.GET.get('godina')
    status = request.GET.get('status', 'aktivne')  # po defaultu aktivne
    # Odredi aktivan status prema odabiru
    aktivan_filter = True if status == 'aktivne' else False

    if mjesec and godina:
        ture = Tura.objects.filter(
            aktivan=aktivan_filter,
            datum_polaska__month=int(mjesec),
            datum_polaska__year=int(godina)
        ).order_by('datum_polaska')
    else:
        ture = Tura.objects.filter(aktivan=aktivan_filter).order_by('datum_polaska')

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
        
        # nove provjere za istekle datume
        if v.registracija_istekla():
            upozorenja.append(f"❌ Vozilu {v.ime} je istekla registracija {v.vrijeme_registracije.strftime('%d.%m.%Y')}!")
        if v.servis_istekao():
            upozorenja.append(f"❌ Vozilo {v.ime} je prošao servis {v.servis.strftime('%d.%m.%Y')}!")

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
        'odabrani_status': status,
    })

@login_required
def unos_ture(request):
    if request.method == 'POST':
        form = TuraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Tura uspješno dodana.")
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

@login_required
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

@login_required
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
            messages.success(request, "✅ Izmjene su uspješno spremljene.")
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
    total_dnevnice = round(ture.aggregate(Sum('dnevnice'))['dnevnice__sum'] or 0, 2)
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

@login_required    
def dodavanje_vozaca(request):
    if request.method == 'POST':
        form = VozacForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('popis_vozaca')
    else:
        form = VozacForm()

    return render(request, 'dodavanje_vozaca.html', {'form': form})

@login_required
def zavrsi_turu(request, tura_id):
    tura = get_object_or_404(Tura, id=tura_id)
    tura.aktivan = False
    tura.save()
    return redirect('homepage')  # Vrati korisnika na popis aktivnih tura

@login_required
def profil_ture(request, tura_id):
    tura = get_object_or_404(Tura, id=tura_id)
    
    if request.method == 'POST':
        form = TuraForm(request.POST, instance=tura)
        if form.is_valid():
            form.save()
            osvjezi_radni_nalog(tura=tura)
            messages.success(request, "✅ Izmjene su uspješno spremljene.")
            return redirect('profil_ture', tura_id=tura.id) # type: ignore
    else:
        form = TuraForm(instance=tura)

    return render(request, 'profil_ture.html', {'tura': tura, 'form': form})

@login_required
def popis_vozila(request):
    vozila = Vozilo.objects.all().order_by('ime')
    return render(request, 'vozila/popis_vozila.html', {'vozila': vozila})

@login_required
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

@login_required
def dodaj_vozilo(request):
    if request.method == 'POST':
        form = VoziloForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('popis_vozila')
    else:
        form = VoziloForm()
    return render(request, 'vozila/dodaj_vozilo.html', {'form': form})

@login_required
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

@login_required
def obrisi_vozilo(request, vozilo_id):
    vozilo = get_object_or_404(Vozilo, id=vozilo_id)
    if request.method == 'POST':
        vozilo.delete()
        return redirect('popis_vozila')
    return render(request, 'vozila/obrisi_vozilo.html', {'vozilo': vozilo})

@login_required
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

@login_required
def obrisi_naputak(request, naputak_id):
    naputak = get_object_or_404(Naputak, id=naputak_id)
    vozilo = naputak.vozilo

    if request.method == 'POST':
        naputak.delete()
        return redirect('detalji_vozila', vozilo_id=vozilo.id)# type: ignore

    return render(request, 'obrisi_naputak.html', {'naputak': naputak, 'vozilo': vozilo})

@login_required
def export_vozac_pdf(request, vozac_id):
    vozac = Vozac.objects.get(id=vozac_id)
    ture = Tura.objects.filter(vozac=vozac).order_by('datum_polaska')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="profil_{vozac.ime}.pdf"'

    # Registriraj font koji podržava hrvatske znakove
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Arial.ttf')
    pdfmetrics.registerFont(TTFont('Arial', font_path))

    doc = SimpleDocTemplate(response, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)# type: ignore
    elements = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TableFont', fontName='Arial', fontSize=9, leading=12))
    styles.add(ParagraphStyle(name='TitleFont', fontName='Arial', fontSize=16, leading=20))

    # Naslov
    naziv_mjeseca = datetime.now().month
    elements.append(Paragraph(f"{vozac.ime} za {naziv_mjeseca}. mjesec", styles['TitleFont']))
    elements.append(Spacer(1, 12))

    # Zaglavlje glavne tablice
    headers = ["Relacija", "Datum polaska", "Datum dolaska", "Prijeđeni km",
               "Zaduženje", "Razduženje", "Razlika", "Iznos ture",
               "Dnevnice", "Čekanje"]
    data = [headers]

    # Redovi tura
    for t in ture:
        row = [
            Paragraph(t.relacija or "", styles['TableFont']),
            Paragraph(t.datum_polaska.strftime('%d.%m.%Y') if t.datum_polaska else "", styles['TableFont']),
            Paragraph(t.datum_dolaska.strftime('%d.%m.%Y') if t.datum_dolaska else "", styles['TableFont']),
            Paragraph(str(t.kilometraza) if t.kilometraza is not None else "", styles['TableFont']),
            Paragraph(str(t.zaduzenje) if t.zaduzenje is not None else "", styles['TableFont']),
            Paragraph(str(t.razduzenje) if t.razduzenje is not None else "", styles['TableFont']),
            Paragraph(str(t.razlika) if t.razlika is not None else "", styles['TableFont']),
            Paragraph(str(t.iznos_ture) if t.iznos_ture is not None else "", styles['TableFont']),
            Paragraph(str(t.dnevnice) if t.dnevnice is not None else "", styles['TableFont']),
            Paragraph(str(t.cekanje) if t.cekanje is not None else "", styles['TableFont']),
        ]
        data.append(row)# type: ignore

    # Ukupni red
    data.append([
        "", "", "",
        Paragraph(str(sum([t.kilometraza or 0 for t in ture])), styles['TableFont']),
        Paragraph(str(sum([t.zaduzenje or 0 for t in ture])), styles['TableFont']),
        Paragraph(str(sum([t.razduzenje or 0 for t in ture])), styles['TableFont']),
        Paragraph(str(sum([t.razlika or 0 for t in ture])), styles['TableFont']),
        Paragraph(str(sum([t.iznos_ture or 0 for t in ture])), styles['TableFont']),
        Paragraph(str(sum([t.dnevnice or 0 for t in ture])), styles['TableFont']),
        Paragraph(str(sum([t.cekanje or 0 for t in ture])), styles['TableFont']),
    ])# type: ignore

    table = Table(data, repeatRows=1, colWidths=[150, 80, 80, 70, 70, 70, 70, 60, 60, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (3,1), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,-1), 'Arial'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    
    col_widths_main = [150,70,70,60,60,60,60,60,60,60]
    x_start_last_col = sum(col_widths_main[:-1])  # počinje zadnja kolona

    # Tablica "Ukupno" (bilanca)
    bilanca = round((sum([t.razlika or 0 for t in ture]) -
                     sum([t.dnevnice or 0 for t in ture]) -
                     sum([t.cekanje or 0 for t in ture]) +
                     vozac.zaduzenje_prethodni_mjesec +
                     vozac.uplaceno_na_banku), 2)

    ukupno_data = [[Paragraph("Ukupno:", styles['TableFont']), Paragraph(str(bilanca) + " " + "KM", styles['TableFont'])]]
    ukupno_table = Table(ukupno_data, colWidths=[60, 60], hAlign='RIGHT')
    ukupno_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),   # oba elementa desno unutar svojih ćelija
        ('FONTNAME', (0,0), (-1,-1), 'Arial'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,-1), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(Spacer(100, 6))
    elements.append(ukupno_table)

    doc.build(elements)
    return response

@login_required
def dodaj_radni_nalog(request):
    if request.method == 'POST':
        form = RadniNalogForm(request.POST)
        if form.is_valid():
            radni_nalog = form.save()
            messages.success(request, "✅ Radni nalog uspješno kreiran.")
            return redirect('radni_nalog_detail', radni_nalog_id=radni_nalog.id)
    else:
        form = RadniNalogForm()
    return render(request, 'radni_nalog/dodaj.html', {'form': form})


@login_required
def radni_nalog_detail(request, radni_nalog_id):
    radni_nalog = get_object_or_404(RadniNalog, id=radni_nalog_id)
    return render(request, 'radni_nalog/detail.html', {'radni_nalog': radni_nalog})


