from django.core.management.base import BaseCommand
from django.db import transaction
from schedule_editor.models import Subject, Schedule, ScheduleItem


class Command(BaseCommand):
    help = 'Delete all subjects and related data from the database'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true',
                          help='Confirm deletion of all data')

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL subjects and related data from the database.\n'
                    'To confirm, run: python manage.py clear_subjects --confirm'
                )
            )
            return

        self.stdout.write('Deleting all subjects and related data...')
        
        try:
            with transaction.atomic():
                # Delete in order to avoid foreign key constraints
                schedule_items_count = ScheduleItem.objects.count()
                schedules_count = Schedule.objects.count()
                subjects_count = Subject.objects.count()
                
                ScheduleItem.objects.all().delete()
                Schedule.objects.all().delete()
                Subject.objects.all().delete()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully deleted:\n'
                        f'- {subjects_count} subjects\n'
                        f'- {schedules_count} schedules\n'
                        f'- {schedule_items_count} schedule items'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error occurred while deleting data: {e}')
            )