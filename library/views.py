from rest_framework import viewsets
from .models import Author, Book, Favorite
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import filters
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, permissions
from rest_framework.exceptions import NotFound
from .serializers import RegisterSerializer, LoginSerializer, AuthorSerializer, BookSerializer, FavoriteSerializer, UserSerializer
from django.contrib.auth import authenticate
from django.db import IntegrityError
from rest_framework import generics
from django.db.models import Q
from .models import Book
from .serializers import BookSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Favorite, Book
from .serializers import FavoriteSerializer, BookSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from .models import Favorite, Book
from django.conf import settings



class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_object(self):
        author_id = self.kwargs.get('pk')
        try:
            return Author.objects.get(author_id=author_id)
        except Author.DoesNotExist:
            raise NotFound(detail="Author not found")


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_object(self):
        book_id = self.kwargs.get('pk')
        try:
            return Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            raise NotFound(detail="Book not found")

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            search_query = str(search_query).strip()
            print(search_query)
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(author_name__icontains=search_query)
            )
        return queryset


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.create_user(
                    username=serializer.validated_data['username'],
                    password=serializer.validated_data['password']
                )
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        return [permissions.IsAdminUser()]


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            max_num = settings.MAX_NUM_FAVORITES
            if Favorite.objects.filter(user=user).count() > int(max_num):
                return Response({"message": "You can have up to 20 favorites"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({"message": "Book ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            book = Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            return Response({"message": "Invalid book ID"}, status=status.HTTP_400_BAD_REQUEST)
        favorite, created = Favorite.objects.get_or_create(user=user, book=book)
        if created:
            return Response({"message": "Book added to favorites"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Book already in favorites"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        book_id = request.data.get('book_id')
        user = request.user
        if not book_id:
            return Response({"message": "Book ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            book = Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            return Response({"message": "Invalid book ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            favorite = Favorite.objects.get(user=user, book=book)
            favorite.delete()
            return Response({"message": "Book removed from favorites"}, status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response({"message": "Favorite entry not found"}, status=status.HTTP_404_NOT_FOUND)


# Τhe idea behind recommended books is that for every one added, there will be up to 2 books of the last 
# added favorite's author and up to 1 favorite of the previous of that favorite, if it exists. The rest of
# recommendations will be the books with the most ratings. Choosing books with the best ratings might have 
# been more reasonable, but better sample-wise-safe than sample-wise-sorry.
@api_view(['GET'])
def recommended_books(request):
    user = request.user
    favorites = Favorite.objects.filter(user=user).order_by('-added_at')
    print(favorites)
    recommended_books = []
    if not favorites:
        return Response({"message": "No favorites found"}, status=status.HTTP_400_BAD_REQUEST)
    elif favorites.count() == 1:
        favorite = Favorite.objects.get(user=user)
        favorite_book_id = favorite.book.book_id
        favorite_author_id = favorite.book.author_id
        available_books = Book.objects.exclude(book_id=favorite_book_id)
        books_of_author = available_books.filter( \
            author_id=favorite_author_id).order_by('-average_rating')[:3]
        count = 5 - books_of_author.count()
        most_ratings_books = available_books.exclude( \
            book_id__in=books_of_author).order_by('-ratings_count').values_list('book_id', flat=True)[:count]
        recommended_books = Book.objects.filter( \
            Q(book_id__in=books_of_author) | Q(book_id__in=most_ratings_books))
    else:  
        favorite_books_ordered = favorites.values_list('book__book_id', flat=True)
        favorite_authors_ordered = favorites.values_list('book__author_id', flat=True)[:2]
        available_books = Book.objects.exclude(book_id__in=favorite_books_ordered)
        books_of_first_author = available_books.filter( \
            author_id=favorite_authors_ordered[0]).order_by('-average_rating')[:2]
        count = 3 - books_of_first_author.count()
        books_of_second_author = available_books.filter( \
            author_id=favorite_authors_ordered[1]).order_by('-average_rating')[:count]
        books_of_authors = Book.objects.filter( \
            Q(book_id__in=books_of_first_author) | Q(book_id__in=books_of_second_author)).values_list('book_id', flat=True)
        count = 5 - books_of_authors.count()
        most_ratings_books = available_books.order_by('-ratings_count').exclude( \
            book_id__in=books_of_authors).values_list('book_id', flat=True)[:count]
        recommended_books = Book.objects.filter( \
            Q(book_id__in=books_of_authors) | Q(book_id__in=most_ratings_books)).distinct()
    serializer = BookSerializer(recommended_books, many=True)
    return Response(serializer.data)


