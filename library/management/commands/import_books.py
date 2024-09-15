import json
import pandas as pd
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from library.models import Book, Author

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def parse_date(self, date_str):
        if date_str:
            try:
                date = pd.to_datetime(date_str, format='%Y-%m-%d', errors='coerce')
                return date.date() if pd.notna(date) else None
            except ValueError:
                return None
        return None

    def handle(self, *args, **options):
        json_file = options['json_file']

        with open(json_file, 'r') as file:
            try:
                for line in file:
                    try:
                        data = json.loads(line)
                        Book.objects.update_or_create(
                            book_id=data.get('id'),
                            defaults={
                                'title': data.get('title', ''),
                                'authors': data.get('authors', ''),
                                'author_id': data.get('author_id', ''),
                                'author_name': data.get('author_name', ''),
                                'work_id': data.get('work_id', ''),
                                'isbn': data.get('isbn', ''),
                                'isbn13': data.get('isbn13', ''),
                                'asin': data.get('asin', ''),
                                'language': data.get('language', ''),
                                'average_rating': data.get('average_rating', 0.0),
                                'rating_dist': data.get('rating_dist', ''),
                                'ratings_count': data.get('ratings_count', 0),
                                'text_reviews_count': data.get('text_reviews_count', 0),
                                'publication_date': self.parse_date(data.get('publication_date')),
                                'original_publication_date': self.parse_date(data.get('original_publication_date')),
                                'book_format': data.get('format', ''),
                                'edition_information': data.get('edition_information', ''),
                                'image_url': data.get('image_url', ''),
                                'publisher': data.get('publisher', ''),
                                'num_pages': data.get('num_pages') if isinstance(data.get('num_pages'), int) else None,
                                'series_id': data.get('series_id', ''),
                                'series_name': data.get('series_name', ''),
                                'series_position': data.get('series_position', ''),
                                'shelves': data.get('shelves', []),
                                'description': data.get('description', ''),
                            }
                        )
                        self.stdout.write(self.style.SUCCESS(f'Successfully imported or updated book with title "{data.get("title")}"'))

                    except json.JSONDecodeError:
                        self.stdout.write(self.style.ERROR('Error decoding JSON object.'))
                    except IntegrityError as e:
                        self.stdout.write(self.style.ERROR(f'Integrity error: {str(e)}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))

            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
