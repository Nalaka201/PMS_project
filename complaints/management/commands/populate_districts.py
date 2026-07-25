from django.core.management.base import BaseCommand
from complaints.models import District


class Command(BaseCommand):
    help = 'Populates all 25 Sri Lankan districts into the database.'

    def handle(self, *args, **options):
        self.stdout.write('Populating Sri Lanka districts...')

        districts = [
            'Colombo',
            'Gampaha',
            'Kalutara',
            'Kandy',
            'Matale',
            'Nuwara Eliya',
            'Galle',
            'Matara',
            'Hambantota',
            'Jaffna',
            'Kilinochchi',
            'Mannar',
            'Mullaitivu',
            'Vavuniya',
            'Trincomalee',
            'Batticaloa',
            'Ampara',
            'Kurunegala',
            'Puttalam',
            'Anuradhapura',
            'Polonnaruwa',
            'Badulla',
            'Monaragala',
            'Ratnapura',
            'Kegalle',
        ]

        created_count = 0
        skipped_count = 0

        for name in districts:
            district, created = District.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created: {name}'))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f'  [SKIP] Already exists: {name}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! {created_count} districts created, {skipped_count} already existed.'
        ))
