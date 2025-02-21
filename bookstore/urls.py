from rest_framework_nested import routers
from .views import *

router = routers.DefaultRouter()

router.register('books', BookViewSet, basename='book')
router.register('genres', GenreViewSet, basename='genre')
router.register('reviews', ReviewViewSet, basename='review')
router.register('carts',CartViewSet,basename='cart')

genres_router = routers.NestedDefaultRouter(router, 'genres', lookup='genre')
genres_router.register('books', BookViewSet, basename='book-genre')
books_router = routers.NestedDefaultRouter(router, 'books', lookup='book')
books_router.register('reviews', ReviewViewSet, basename='book-review')

urlpatterns = [
              ] + router.urls + genres_router.urls + books_router.urls
