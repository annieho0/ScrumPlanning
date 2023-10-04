from .models import CustomizedUser
from django.contrib.auth.backends import BaseBackend

class UserAuthentication(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        
        try:
            user = CustomizedUser.objects.get(email=email)
            if user.check_password(password):
                return user
            return None
        except CustomizedUser.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        try:
            return CustomizedUser.objects.get(pk=user_id)
        except:
            return None
        