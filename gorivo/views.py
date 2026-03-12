from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Tank, TransakcijaGoriva
from .forms import PotrosnjaForm, RefillForm, RaspodjelaForm

def gorivo_view(request):
    tank = Tank.objects.first()
    if not tank:
        tank = Tank.objects.create()

    potrosnja_form = PotrosnjaForm()
    refill_form = RefillForm()
    raspodjela_form = RaspodjelaForm(tank=tank)

    context = {
        "tank": tank,
        "potrosnja_form": potrosnja_form,
        "refill_form": refill_form,
        "form_raspodjela": raspodjela_form,
        "transakcije": tank.transakcije.order_by("-datum")[:20],
    }
    return render(request, "gorivo/gorivo.html", context)


def dodaj_potrosnju(request):
    tank = Tank.objects.first()
    if not tank:
        tank = Tank.objects.create()

    if request.method == "POST":
        form = PotrosnjaForm(request.POST)
        if form.is_valid():
            transakcija = form.save(commit=False)
            transakcija.tank = tank
            transakcija.tip = "potrosnja"
            transakcija.drzava = request.POST.get("drzava")  # bih ili rh
            transakcija.save()
    return redirect("gorivo")


def dodaj_refill(request):
    tank = Tank.objects.first()

    if not tank:
        tank = Tank.objects.create()

    if request.method == "POST":
        form = RefillForm(request.POST, instance=tank)

        if form.is_valid():

            bih = form.cleaned_data.get("bih_gorivo") or 0
            rh = form.cleaned_data.get("rh_gorivo") or 0

            ukupno_za_dodati = bih + rh
            trenutno = tank.ukupno_stanje

            # PROVJERA KAPACITETA
            if trenutno + ukupno_za_dodati > tank.kapacitet:

                slobodno = tank.kapacitet - trenutno

                messages.error(
                    request,
                    f"Nema dovoljno mjesta u tanku. "
                    f"Slobodno je još {slobodno} L."
                )

                return redirect("gorivo")

            # dodaj refill BIH
            if bih > 0:
                TransakcijaGoriva.objects.create(
                    tank=tank,
                    tip="refill",
                    drzava="bih",
                    kolicina=bih,
                    napomena="Punjenje tanka BiH"
                )

            # dodaj refill RH
            if rh > 0:
                TransakcijaGoriva.objects.create(
                    tank=tank,
                    tip="refill",
                    drzava="rh",
                    kolicina=rh,
                    napomena="Punjenje tanka RH"
                )

            # update kapaciteta ako je promijenjen
            tank.kapacitet = form.cleaned_data.get("kapacitet", tank.kapacitet)
            tank.save()

            messages.success(request, "Punjenje tanka uspješno spremljeno.")

    return redirect("gorivo")

def raspodjela_view(request):
    tank = Tank.objects.first()
    if not tank:
        tank = Tank.objects.create()

    if request.method == "POST":
        form = RaspodjelaForm(request.POST, tank=tank)
        if form.is_valid():
            # Prvo resetiramo sve raspodjele goriva
            tank.transakcije.filter(tip="raspodjela").delete()

            # Dohvatimo unose
            bih = form.cleaned_data["bih_gorivo"]
            rh = form.cleaned_data["rh_gorivo"]

            # Ako je uneseno > 0, kreiramo transakcije sa tip="raspodjela"
            if bih > 0:
                TransakcijaGoriva.objects.create(
                    tank=tank,
                    tip="potrosnja",  # Ovdje koristimo potrosnja za oduzimanje
                    drzava="bih",
                    kolicina=bih,
                    napomena="Potrošeno gorivo BiH"
                )
            if rh > 0:
                TransakcijaGoriva.objects.create(
                    tank=tank,
                    tip="potrosnja",
                    drzava="rh",
                    kolicina=rh,
                    napomena="Potrošeno gorivo RH"
                )

            # Ukupni kapacitet samo update ako se promijeni
            tank.kapacitet = form.cleaned_data["kapacitet"]
            tank.save()
            return redirect("gorivo")
    else:
        form = RaspodjelaForm(tank=tank)

    return render(request, "gorivo/raspodjela.html", {"form": form})