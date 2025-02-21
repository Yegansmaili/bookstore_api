import uuid

from django.db import models
from django.conf import settings
from uuid import uuid4


class Genre(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(allow_unicode=True, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=500)
    slug = models.SlugField(allow_unicode=True, unique=True)
    description = models.TextField()
    author = models.CharField(max_length=300)
    file = models.FileField(upload_to='books/')
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, related_name='books')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    BOOK_STAR = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    star = models.CharField(choices=BOOK_STAR)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user}-{self.book} : {self.star}'


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    book = models.ForeignKey(Book, related_name='cart_items', on_delete=models.CASCADE)

    class Meta:
        unique_together = [['cart', 'book']]

    def __str__(self):
        return f'{self.cart} : {self.book}'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    is_paid = models.BooleanField(default=False)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id


class OrderItem(models.Model):
    order = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='order_items')
    book = models.ForeignKey(Book, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = [['order', 'book']]

    def __str__(self):
        return f'{self.order} : {self.book}'
