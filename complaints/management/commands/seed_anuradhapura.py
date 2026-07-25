from django.core.management.base import BaseCommand
from complaints.models import District, PradeshiyaSabha


class Command(BaseCommand):
    help = 'Seeds Anuradhapura Pradeshiya Sabhas into the database.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Anuradhapura Pradeshiya Sabhas...')

        # Get or create Anuradhapura district
        district, created = District.objects.get_or_create(name='Anuradhapura')
        if created:
            self.stdout.write('Created District: Anuradhapura')
        else:
            self.stdout.write('District found: Anuradhapura')

        sabhas = [
            'Galenbindunuwewa',
            'Horowpothana',
            'Ipalogama',
            'Kahatagasdigiliya',
            'Kebithigollewa',
            'Kekirawa',
            'Mahavilachchiya',
            'Medawachchiya',
            'Mihinthale',
            'Nachchadoowa',
            'Nochchiyagama',
            'Nuwaragam Palatha Central',
            'Nuwaragam Palatha East',
            'Padaviya',
            'Palagala',
            'Palugaswewa',
            'Rajanganaya',
            'Rambewa',
            'Thalawa',
            'Thambuttegama',
            'Thirappane',
        ]

        created_count = 0
        skipped_count = 0

        for name in sabhas:
            sabha, created = PradeshiyaSabha.objects.get_or_create(
                name=name,
                district=district
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created: {name}'))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f'  [SKIP] Already exists: {name}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! {created_count} Pradeshiya Sabhas created, {skipped_count} already existed.'
        ))
