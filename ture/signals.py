from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vozac, Tura

@receiver(post_save, sender=Vozac)
def azuriraj_ture_vozaca(sender, instance, **kwargs):
    """
    Signal koji se poziva nakon spremanja Vozac objekta.
    Ponovno računa dnevnice za sve ture tog vozača.
    """
    ture_vozaca = Tura.objects.filter(vozac=instance)
    for t in ture_vozaca:
        t.save(update_fields=['dnevnice'])  # ovo poziva Tura.save i preračunava dnevnice
