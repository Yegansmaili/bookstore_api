from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser

from .models import *

from rest_framework.response import Response
from rest_framework import status, mixins
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .permissions import IsAdminOrReadOnly
from .serializers import *


class BookViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddBookSerializer
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UpdateBookSerializer
        return BookSerializer

    def get_queryset(self):
        queryset = Book.objects.select_related('genre').prefetch_related('reviews').all()
        genre_slug = self.kwargs.get('genre_pk')
        if genre_slug is not None:
            queryset = queryset.filter(genre__slug=genre_slug).all()
        return queryset

    def create(self, request, *args, **kwargs):
        create_book_serializer = AddBookSerializer(data=request.data)
        create_book_serializer.is_valid(raise_exception=True)
        created_book = create_book_serializer.save()
        serializer = BookSerializer(created_book)
        return Response(serializer.data)


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.prefetch_related('books').all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]


class ReviewViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.select_related('book', 'user').all()
        book_slug = self.kwargs.get('book_pk')
        if book_slug is not None:
            queryset = queryset.filter(book__slug=book_slug).all()
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddReviewSerializer
        if self.request.method == 'PATCH' or self.request.method == 'PUT':
            return UpdateReviewSerializer
        return ReviewSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def create(self, request, *args, **kwargs):
        create_review_serializer = AddReviewSerializer(data=request.data,
                                                       context={'user_id': self.request.user.id})
        create_review_serializer.is_valid(raise_exception=True)
        created_review = create_review_serializer.save()
        serializer = ReviewSerializer(created_review)
        return Response(serializer.data)


class CartViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet,
                  mixins.DestroyModelMixin):
    queryset = Cart.objects.prefetch_related('cart_items__book').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        cart_pk = self.kwargs.get('cart_pk')
        return CartItem.objects.select_related('cart', 'book__genre').filter(cart__pk=cart_pk).all()

    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk'], }

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        return CartItemSerializer

    def create(self, request, *args, **kwargs):
        created_item_serializer = AddCartItemSerializer(
            data=request.data,
            context={'cart_pk': self.kwargs['cart_pk']}
        )
        created_item_serializer.is_valid(raise_exception=True)
        created_item = created_item_serializer.save()
        serializer = CartItemSerializer(created_item)
        return Response(serializer.data)
