from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .models import Book

from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .permissions import IsAdminOrReadOnly
from .serializers import *


class BookViewSet(ModelViewSet):
    queryset = Book.objects.select_related('genre').all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddBookSerializer
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UpdateBookSerializer
        return BookSerializer

    def create(self, request, *args, **kwargs):
        create_book_serializer = AddBookSerializer(data=request.data)
        create_book_serializer.is_valid(raise_exception=True)
        created_book = create_book_serializer.save()
        serializer = BookSerializer(created_book)
        return Response(serializer.data)


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
