from django.db import models
from django.conf import settings

class Author(models.Model):
    author_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    fans_count = models.IntegerField(default=0, blank=True, null=True)
    ratings_count = models.IntegerField(default=0, blank=True, null=True)
    average_rating = models.FloatField(default=0.0, blank=True, null=True)
    text_reviews_count = models.IntegerField(default=0)
    work_ids = models.JSONField(blank=True, null=True)  
    book_ids = models.JSONField(blank=True, null=True)  
    works_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Book(models.Model):
    book_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255, null=True, blank=True)
    authors = models.JSONField(blank=True, null=True)
    author_id = models.CharField(max_length=255, null=True, blank=True)
    author_name = models.CharField(max_length=255, null=True, blank=True)
    work_id = models.CharField(max_length=255, blank=True, null=True)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    isbn13 = models.CharField(max_length=13, blank=True, null=True)
    asin = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=10, blank=True, null=True)
    average_rating = models.FloatField(default=0.0)
    rating_dist = models.TextField(blank=True, null=True)  
    ratings_count = models.IntegerField(default=0, blank=True, null=True)
    text_reviews_count = models.IntegerField(default=0, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True) 
    original_publication_date = models.DateField(blank=True, null=True)  
    book_format = models.CharField(max_length=50, blank=True, null=True)
    edition_information = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    num_pages = models.IntegerField(blank=True, null=True)
    series_id = models.CharField(max_length=255, blank=True, null=True)
    series_name = models.CharField(max_length=255, blank=True, null=True)
    series_position = models.CharField(max_length=10, blank=True, null=True)
    shelves = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')
    
    def __str__(self):
        return f"{self.user} - {self.book}"

