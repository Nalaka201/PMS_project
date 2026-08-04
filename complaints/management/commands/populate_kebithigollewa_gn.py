from django.core.management.base import BaseCommand
from complaints.models import District, PradeshiyaSabha, Wasama


class Command(BaseCommand):
    help = 'Populates GN Divisions (Wasamas) for Kebithigollewa Pradeshiya Sabha.'

    def handle(self, *args, **options):
        self.stdout.write('Populating Kebithigollewa GN Divisions...')

        # Get Anuradhapura district
        try:
            district = District.objects.get(name='Anuradhapura')
        except District.DoesNotExist:
            self.stdout.write(self.style.ERROR('ERROR: Anuradhapura district not found. Run populate_anuradhapura first.'))
            return

        # Get Kebithigollewa Pradeshiya Sabha
        # Try both possible name formats
        sabha = None
        for name_try in ['Kebithigollewa Pradeshiya Sabha', 'Kebithigollewa']:
            try:
                sabha = PradeshiyaSabha.objects.get(name=name_try, district=district)
                break
            except PradeshiyaSabha.DoesNotExist:
                continue

        if not sabha:
            self.stdout.write(self.style.ERROR('ERROR: Kebithigollewa PS not found. Run populate_all_srilanka or populate_anuradhapura first.'))
            return

        self.stdout.write(f'Found: {sabha}')

        # GN Divisions for Kebithigollewa PS
        # Format: (name, code)
        gn_divisions = [
            ('Halmillawetiya', 'D 01'),
            ('Kanugahawewa', 'D 02'),
            ('Herathhalmillewa', 'D 03'),
            ('Wahalkada East', 'D 04'),
            ('Wahalkada Central', 'D 05'),
            ('Wahalkada West', 'D 06'),
            ('Bellankadawala', 'D 07'),
            ('Punchimudagama', 'D 08'),
            ('Kahatagollewa', 'D 09'),
            ('Thammennawa', 'D 10'),
            ('Kunchuttuwa', 'D 11'),
            ('Galawewa', 'D 12'),
            ('Thittagonewa', 'D 13'),
            ('Kurulugama', 'D 14'),
            ('Sinhala Etaweerawewa', 'D 15'),
            ('Ethalvidda Wewa', 'D 16'),
            ('Gonumeriyawa', 'D 17'),
            ('Kebithigollewa Town', 'D 18'),
            ('Ihala Usgollewa', 'D 19'),
            ('Aiyathigewewa', 'D 20'),
            ('Bandaraulpatha', 'D 21'),
            ('Kiriketuwewa', 'D 22'),
            ('Gonahathdenawa', 'D 23'),
            ('Thimbiriwewa', 'D 24'),
            ('Handagala Kirimetiyawa', 'D 25'),
            ('Wattewewa', 'D 26'),
        ]

        created_count = 0
        skipped_count = 0

        for name, code in gn_divisions:
            wasama, created = Wasama.objects.get_or_create(
                name=name,
                pradeshiya_sabha=sabha,
                defaults={'code': code}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created: {name} ({code})'))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f'  [SKIP] Already exists: {name}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! {created_count} GN Divisions created, {skipped_count} already existed.'
        ))
