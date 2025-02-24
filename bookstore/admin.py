from django.contrib import admin

from .models import *


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'author', 'datetime_created','averaged_review']
    prepopulated_fields = {'slug': ('name',), }


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    prepopulated_fields = {'slug': ('name',), }


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    ...


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    ...


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    ...


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ...


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    ...
