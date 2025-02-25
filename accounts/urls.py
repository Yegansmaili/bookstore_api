from django.urls import path
from .views import LoginView, VerifyOtpView
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register('login', LoginView, basename='login')
router.register('verify', VerifyOtpView, basename='verify')

urlpatterns = [

              ] + router.urls
