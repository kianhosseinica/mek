import re
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class PhoneOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        user = None
        phone_regex = re.compile(r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$')

        # Admin login explicitly with phone number
        if request.path.startswith('/admin'):
            cleaned_phone = re.sub(r'\D', '', username)
            try:
                user = User.objects.get(phone_number=cleaned_phone, is_staff=True)
            except User.DoesNotExist:
                return None
        else:
            # User can log in via phone number or email
            if phone_regex.match(username):
                cleaned_phone = re.sub(r'\D', '', username)
                try:
                    user = User.objects.get(phone_number=cleaned_phone)
                except User.DoesNotExist:
                    return None
            else:
                try:
                    user = User.objects.get(email__iexact=username)
                except User.DoesNotExist:
                    return None

        if user and user.check_password(password):
            return user
        return None
