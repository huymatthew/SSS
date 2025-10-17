import re
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from schedule_editor.models import Subject


class Command(BaseCommand):
    help = 'Import subjects from data.txt file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='data.txt',
                          help='Path to the data file (default: data.txt)')
        parser.add_argument('--clear', action='store_true',
                          help='Clear existing subjects before importing')

    def handle(self, *args, **options):
        file_path = options['file']
        
        if options['clear']:
            self.stdout.write('Clearing existing subjects...')
            Subject.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared all subjects'))

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File {file_path} not found'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {e}'))
            return

        self.stdout.write(f'Processing {len(lines)} lines...')
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        # Colors for subjects
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', 
                 '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#f1c40f']

        with transaction.atomic():
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Parse the line format: code`name`credits`professor`day_time_room`weeks
                    parts = line.split('`')
                    if len(parts) < 6:
                        self.stdout.write(f'Skipping line {line_num}: Invalid format')
                        skipped_count += 1
                        continue
                    
                    code = parts[0].strip()
                    name = parts[1].strip()
                    credits_str = parts[2].strip()
                    professor = parts[3].strip()
                    day_time_room = parts[4].strip()
                    weeks = parts[5].strip()
                    
                    # Parse credits
                    try:
                        credits = int(credits_str) if credits_str.isdigit() else 3
                    except:
                        credits = 3
                    
                    # Parse day, time and room from day_time_room
                    # Format: "Thứ 2: 6-8,P1" or "Thứ 5: 8-9,B108"
                    day = None
                    startperiod = None
                    endperiod = None
                    room = ""
                    
                    if ':' in day_time_room:
                        day_part, time_room_part = day_time_room.split(':', 1)
                        
                        # Parse day
                        day_mapping = {
                            'Thứ 2': 1, 'Thứ 3': 2, 'Thứ 4': 3, 'Thứ 5': 4,
                            'Thứ 6': 5, 'Thứ 7': 6, 'Chủ Nhật': 7
                        }
                        
                        for day_name, day_num in day_mapping.items():
                            if day_name in day_part:
                                day = day_num
                                break
                        
                        # Parse time and room
                        if ',' in time_room_part:
                            time_part, room = time_room_part.split(',', 1)
                            room = room.strip()
                        else:
                            time_part = time_room_part
                        
                        time_part = time_part.strip()
                        
                        # Parse time periods (e.g., "6-8" -> startperiod=6, endperiod=8)
                        if '-' in time_part:
                            try:
                                start_str, end_str = time_part.split('-', 1)
                                startperiod = int(start_str.strip())
                                endperiod = int(end_str.strip())
                            except:
                                pass
                    
                    # Generate semester info (assuming current semester is 1-2025)
                    semester = "1-2025"
                    
                    # Check if subject already exists
                    if Subject.objects.filter(code=code).exists():
                        self.stdout.write(f'Skipping line {line_num}: Subject {code} already exists')
                        skipped_count += 1
                        continue
                    
                    # Create subject
                    subject = Subject.objects.create(
                        name=name,
                        code=code,
                        credits=credits,
                        professor=professor,
                        startperiod=startperiod,
                        endperiod=endperiod,
                        day=day,
                        room=room,
                        color=random.choice(colors),
                        semester=semester,
                        weeks=weeks
                    )
                    
                    created_count += 1
                    
                    if created_count % 100 == 0:
                        self.stdout.write(f'Processed {created_count} subjects...')
                        
                except Exception as e:
                    self.stdout.write(f'Error processing line {line_num}: {e}')
                    self.stdout.write(f'Line content: {line}')
                    error_count += 1
                    continue

        self.stdout.write(self.style.SUCCESS(
            f'Import completed!\n'
            f'Created: {created_count} subjects\n'
            f'Skipped: {skipped_count} subjects\n'
            f'Errors: {error_count} subjects'
        ))