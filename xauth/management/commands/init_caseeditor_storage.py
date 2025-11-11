"""
Management command to initialize Case Editor storage with example data
"""
from django.core.management.base import BaseCommand
from xauth.file_manager import file_manager


class Command(BaseCommand):
    help = 'Initialize Case Editor storage with example data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing Case Editor storage...')
        
        try:
            file_manager.initialize_example_data()
            self.stdout.write(self.style.SUCCESS(
                'Successfully initialized Case Editor storage with example data'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Failed to initialize storage: {e}'
            ))

