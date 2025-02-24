import django_filters
from django.db.models import Avg, IntegerField, Subquery
from django.db.models.functions import Cast

from .models import Book, Review


class BookFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    highly_rated_books = django_filters.NumberFilter(method='highly_rated_books_method')

    class Meta:
        model = Book
        fields = ['min_price', 'max_price',]


