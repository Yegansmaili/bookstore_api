from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser
from . import helper
from .permissions import IsAdminOrPostOnly
from .serializers import CustomUserSerializer, CustomUserOtpSerializer


class LoginView(ModelViewSet):
    http_method_names = ['get', 'post']
    permission_classes = [IsAdminOrPostOnly]
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


    def create(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
        # create or get the existing user
        user, created = CustomUser.objects.get_or_create(phone_number=phone_number)

        otp = helper.get_random_otp()
        helper.send_otp_code(phone_number, otp)
        if created:
            user.is_active = False
        user.otp_code = otp
        user.save()
        request.session['phone_number'] = phone_number
        return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)


class VerifyOtpView(ModelViewSet):
    http_method_names = ['post']
    serializer_class = CustomUserOtpSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAdminOrPostOnly]


    def create(self, request, *args, **kwargs):
        serializer = CustomUserOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            phone_number = request.session.get('phone_number')
            user = CustomUser.objects.get(phone_number=phone_number)
            otp = serializer.validated_data['otp_code']

            if not helper.check_otp_expiration(phone_number):
                return Response('the otp has expired')
            if not user.otp_code == otp:
                return Response('the otp is incorrect! Try again.')

            user.is_active = True
            user.save()
            # login(request, user)

            # create tokens
            refresh = RefreshToken.for_user(user)
            del request.session['phone_number']

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response('an error occurred, please try again!')
