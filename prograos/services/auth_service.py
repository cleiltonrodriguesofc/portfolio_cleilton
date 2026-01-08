from django.contrib.auth import get_user_model

User = get_user_model()


class AuthService:
    @staticmethod
    def register_user(form):
        """
        Registers a new user but sets is_active=False requiring admin approval.
        """
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        return user
