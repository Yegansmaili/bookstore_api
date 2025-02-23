from django.contrib.auth import get_user_model
from django.db.models import Subquery, Exists, OuterRef, Count
from django.http import FileResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, IsAuthenticated
from rest_framework.reverse import reverse
from rest_framework.views import APIView

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

    def destroy(self, request, *args, **kwargs):
        book = self.get_object()
        if book.order_items.count() > 0:
            return Response('some order items have this book',
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET', 'HEAD', 'OPTIONS'], permission_classes=[IsAuthenticated])
    def suggest(self, request):
        user_reviews = Review.objects.select_related('book__genre', 'user').filter(user_id=self.request.user.id,
                                                                                   star__gt=3).all()
        genres = user_reviews.values_list('book__genre', flat=True).distinct()
        books = user_reviews.values_list('book', flat=True)
        suggested_books = self.get_queryset().filter(genre__in=Subquery(genres)).exclude(id__in=[books])[:4]

        serializer = SuggestGenresSerializer(suggested_books, many=True)
        return Response(serializer.data)


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.prefetch_related('books').all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]


class ReviewViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.select_related('book__genre').all()
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


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options', 'post', 'delete']

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.prefetch_related('order_items__book').all()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user_id=self.request.user.id)

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def create(self, request, *args, **kwargs):
        create_order_serializer = CreateOrderSerializer(data=request.data,
                                                        context={'user_id': self.request.user.id})
        create_order_serializer.is_valid(raise_exception=True)
        created_order = create_order_serializer.save()
        serializer = OrderSerializer(created_order)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        if order.order_items.count() > 0:
            return Response('There are some items in this order',
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderItemViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options', 'delete']
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        order_id = self.kwargs['order_pk']
        return OrderItem.objects.select_related('order', 'book').filter(order_id=order_id).all()

    def list(self, request, *args, **kwargs):
        items = self.get_queryset()
        serializer = OrderItemSerializer(items, many=True)
        download_links = {
            item.book.name: request.build_absolute_uri(reverse('file-download', args=[item.book.slug]))
            for item in items
        }
        response_data = {
            'items': serializer.data,
            'download_links': download_links
        }
        return Response(response_data, status=200)


class DownloadFileView(APIView):
    def get(self, request, slug):
        try:
            book = Book.objects.get(slug=slug)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

        if not book.file:
            return Response({'error': 'File Url not found'}, status=status.HTTP_404_NOT_FOUND)

        file_path = book.file.path
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{book.file.name}"'
        return response
