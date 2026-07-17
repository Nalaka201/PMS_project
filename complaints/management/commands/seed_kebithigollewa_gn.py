from django.core.management.base import BaseCommand
from complaints.models import District, PradeshiyaSabha, Wasama


class Command(BaseCommand):
    help = 'Seeds GN Divisions (Wasamas) for Kebithigollewa Pradeshiya Sabha.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Kebithigollewa GN Divisions...')

        # Get Anuradhapura district
        try:
            district = District.objects.get(name='Anuradhapura')
        except District.DoesNotExist:
            self.stdout.write(self.style.ERROR('ERROR: Anuradhapura district not found. Run seed_anuradhapura first.'))
            return

        # Get Kebithigollewa Pradeshiya Sabha
        try:
            sabha = PradeshiyaSabha.objects.get(name='Kebithigollewa', district=district)
        except PradeshiyaSabha.DoesNotExist:
            self.stdout.write(self.style.ERROR('ERROR: Kebithigollewa PS not found. Run seed_anuradhapura first.'))
            return

        self.stdout.write(f'Found: {sabha}')

        # GN Divisions for Kebithigollewa PS
        # Format: (name, code) - code is empty if not specified
        gn_divisions = [
            ('Halmillawetiya', ''),
            ('Kanugahawewa', ''),
            ('Herathhalmillewa', ''),
            ('Bellankadawala', ''),
            ('Punchimudagama', ''),
            ('Wahalkada', 'D 06'),
            ('Wahalkada', 'D 05'),
            ('Wahalkada', 'D 04'),
            ('Kahatagollewa', ''),
            ('Thammennawa', ''),
            ('Kunchuttuwa', ''),
            ('Galawewa', ''),
            ('Thittagonewa', ''),
            ('Kurulugama', ''),
            ('Sinhala Etaweerawewa', ''),
            ('Ethalvidda Wewa', ''),
            ('Gonumeriyawa', ''),
            ('Kebithigollewa', ''),
            ('Ihala Usgollewa', ''),
            ('Aiyathigewewa', ''),
            ('Bandaraulpatha', ''),
            ('Kiriketuwewa', ''),
            ('Gonahathdenawa', ''),
            ('Thimbiriwewa', ''),
            ('Handagala Kirimetiyawa', ''),
            ('Wattewewa', ''),
        ]

        created_count = 0
        skipped_count = 0

        for name, code in gn_divisions:
            display_name = f'{code} {name}'.strip() if code else name
            wasama, created = Wasama.objects.get_or_create(
                name=display_name,
                pradeshiya_sabha=sabha,
                defaults={'code': code}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created: {display_name}'))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f'  [SKIP] Already exists: {display_name}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! {created_count} GN Divisions created, {skipped_count} already existed.'
        ))
