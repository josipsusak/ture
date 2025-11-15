# ture/migrations/0003_populate_cijene_dnevnica.py
from django.db import migrations

def populate_cijene(apps, schema_editor):
    CijenaDnevnica = apps.get_model('ture', 'CijenaDnevnica')
    
    default_cijene = [
        ('BiH', 12.5), ('Austrija', 90), ('Njemacka', 90),
        ('Slovenija', 80), ('Francuska', 90), ('Hrvatska', 50),
        ('Madjarska', 70), ('Svicarska', 90), ('Italija', 80),
    ]
    
    for drzava, iznos in default_cijene:
        CijenaDnevnica.objects.update_or_create(
            drzava=drzava,
            defaults={'iznos': iznos}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('ture', '0017_cijenadnevnica'),  # ← OVO MORA BITI PRETHODNA MIGRACIJA
    ]

    operations = [
        migrations.RunPython(populate_cijene, reverse_code=migrations.RunPython.noop),
    ]