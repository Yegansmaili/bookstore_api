from accounts.models import CustomUser


class PhoneAuthenticationBackend:
    @staticmethod
    def authenticate(request, phone_number=None, password=None):
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
            return user
        except CustomUser.DoesNotExist:
            return None

    @staticmethod
    def get_user(user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            return user
        except CustomUser.DoesNotExist:
            return None
