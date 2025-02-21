from django.utils.text import slugify
from rest_framework import serializers
from .models import *


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id','name', 'description']

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
        return Review.objects.create(user_id=user_id, **validated_data)
