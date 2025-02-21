from rest_framework_nested import routers
from .views import *

router = routers.DefaultRouter()

router.register('books', BookViewSet, basename='book')
router.register('genres', GenreViewSet, basename='genre')
router.register('reviews', ReviewViewSet, basename='review')

urlpatterns = [
              ] + router.urls
