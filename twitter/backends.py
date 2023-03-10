from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import re

UserModel = get_user_model()

class MyBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):

        if '@' in username:
            kwargs = {'email': username}
            #if nothing but digits, look for a phone number
        # elif not bool(re.findall(r'\D',username)):
        #     kwargs = {'phone': username}
        else:
            kwargs = {'username': username}

        #i dont really understand this block
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return

        try:
            user = UserModel._default_manager.get(**kwargs)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user