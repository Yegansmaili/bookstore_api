from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.http import urlencode
from django.urls import reverse

from .models import *


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['name', 'genre', 'price', 'author', 'averaged_review']
    prepopulated_fields = {'slug': ('name',), }
    list_per_page = 10
    list_editable = ['price']
    list_filter = ['datetime_created']
    search_fields = ['name']
    list_select_related = ['genre']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('reviews')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'num_of_books']
    prepopulated_fields = {'slug': ('name',), }
    list_per_page = 10
    search_fields = ['name']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(num_of_books=Count('books'))

    @admin.display(description='books num')
    def num_of_books(self, genre):
        url = (
                reverse('admin:bookstore_book_changelist') + '?'
                + urlencode({'genre_id': genre.id})
        )
        return format_html('<a href={}>{}</a>', url, genre.num_of_books)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'star']
    list_per_page = 10
    ordering = ['star', 'book']
    list_filter = ['star']
    search_fields = ['book__name']
    list_select_related = ['book', 'user']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'num_of_items', 'total']
    list_per_page = 10
    list_filter = ['created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('cart_items__book').annotate(
            num_of_books=Count('cart_items'))

    @admin.display(description='items num')
    def num_of_items(self, cart):
        url = (
                reverse('admin:bookstore_cartitem_changelist') + '?'
                + urlencode({'cart_id': cart.id})
        )
        return format_html('<a href={}>{}</a>', url, cart.num_of_books)

    def total(self, cart):
        return sum(item.book.price for item in cart.cart_items.all())


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'book', ]
    list_per_page = 10
    list_select_related = ['book', 'cart']
    search_fields = ['book__name']
    list_filter = ['cart__created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'num_of_items', 'total']
    list_per_page = 10
    list_filter = ['datetime_modified']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('order_items').annotate(num_of_books=Count('order_items'))

    @admin.display(description='items num')
    def num_of_items(self, order):
        url = (
                reverse('admin:bookstore_orderitem_changelist') + '?'
                + urlencode({'order_id': order.id})
        )
        return format_html('<a href={}>{}</a>', url, order.num_of_books)

    def total(self, order):
        return sum(item.price for item in order.order_items.all())


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'book', 'price', ]
    list_per_page = 10
    list_select_related = ['book', 'order']
    search_fields = ['book__name']
    list_filter = ['order__datetime_modified']
