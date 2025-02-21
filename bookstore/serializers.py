from django.utils.text import slugify
from rest_framework import serializers
from .models import *


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description']

    def create(self, validated_data):
        name = validated_data.get('name')
        slug = slugify(name, allow_unicode=True)
        genre = Genre.objects.create(slug=slug, **validated_data)

        self.instance = genre
        return genre


class BookGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']


class BookSerializer(serializers.ModelSerializer):
    genre = BookGenreSerializer()

    class Meta:
        model = Book
        fields = ['id', 'name', 'description', 'author', 'genre', 'price']


class UpdateBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['price']


class AddBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['name', 'description', 'author', 'genre', 'file', 'price']

    def create(self, validated_data):
        book = Book(**validated_data)
        book.slug = slugify(book.name, allow_unicode=True)
        book.save()
        return book


class BookReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['name']


class ReviewSerializer(serializers.ModelSerializer):
    book = BookReviewSerializer()

    class Meta:
        model = Review
        fields = ['star', 'book', 'content']


class AddReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['star', 'book', 'content']

    def create(self, validated_data):
        user_id = self.context['user_id']
        book = validated_data.get('book')
        star = validated_data.get('star')
        content = validated_data.get('content')
        try:
            review_obj = Review.objects.get(user_id=user_id, book_id=book.id)
            review_obj.star = star
            review_obj.content = content
            review_obj.save()

        except Review.DoesNotExist:
            review_obj = Review.objects.create(user_id=user_id, **validated_data)

        return review_obj


class UpdateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['star', 'content']


class BookItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['name', 'price']


class CartItemSerializer(serializers.ModelSerializer):
    book = BookItemSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'book']


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'book']

    def create(self, validated_data):
        cart_id = self.context['cart_pk']
        return CartItem.objects.create(cart_id=cart_id, **validated_data)


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    def get_total(self, cart):
        return sum(item.book.price for item in cart.cart_items.all())

    class Meta:
        model = Cart
        fields = ['id', 'cart_items', 'total']
        read_only_fields = ['id']
