# prograos/utils_demo.py
from django.conf import settings
from django.contrib.auth import get_user_model

def get_demo_user():
    """
    returns demo user. creates if not exists.
    uses unusable password to avoid accidental login.
    """
    User = get_user_model()

    # if prefer binding by id:
    if hasattr(settings, "DEMO_USER_ID"):
        demo = User.objects.get(pk=settings.DEMO_USER_ID)
        if not demo.has_usable_password():
            demo.set_unusable_password()
            demo.save(update_fields=["password"])
        return demo

    username = getattr(settings, "DEMO_USER_USERNAME", "tester")
    demo, _created = User.objects.get_or_create(
        username=username,
        defaults={"is_active": True},
    )
    if not demo.has_usable_password():
        demo.set_unusable_password()
        demo.save(update_fields=["password"])
    return demo


def get_actor(request):
    """
    resolves data "owner" of this request:
      - if authenticated, uses request.user;
      - else, uses tester user.
    """
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        return user
    # public/anonymous -> uses tester
    return get_demo_user()
