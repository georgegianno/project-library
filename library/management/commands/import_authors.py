import json
from django.core.management.base import BaseCommand
from library.models import Author

class Command(BaseCommand):
    help = 'Import authors from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **options):
        json_file = options['json_file']
        with open(json_file, 'r') as file:
            try:
                for line in file:
                    try:
                        data = json.loads(line)
                        Author.objects.update_or_create(
                            author_id=data.get('id'),
                            defaults={
                                'name': data.get('name', ''),
                                'gender': data.get('gender', ''),
                                'image_url': data.get('image_url', ''),
                                'about': data.get('about', ''),
                                'fans_count': data.get('fans_count', 0),
                                'ratings_count': data.get('ratings_count', 0),
                                'average_rating': data.get('average_rating', 0.0),
                                'text_reviews_count': data.get('text_reviews_count', 0),
                                'work_ids': data.get('work_ids', []),
                                'book_ids': data.get('book_ids', []),
                                'works_count': data.get('works_count', 0),
                            }
                        )
                        self.stdout.write(self.style.SUCCESS(f'Successfully imported or updated author with name "{data.get("name")}"'))
                    
                    except json.JSONDecodeError:
                        self.stdout.write(self.style.ERROR('Error decoding JSON object.'))
            
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
