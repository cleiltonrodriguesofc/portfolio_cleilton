# prograos/utils_demo.py
from django.conf import settings
from django.contrib.auth import get_user_model

def get_demo_user():
    """
    Retorna o usuário de demonstração. Cria se não existir.
    Usa senha inutilizável para evitar login acidental.
    """
    User = get_user_model()

    # Se preferir amarrar por ID:
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
    Resolve o "dono" dos dados desta request:
      - se estiver autenticado, usa request.user;
      - senão, usa o usuário tester.
    """
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        return user
    # público/anônimo → usa tester
    return get_demo_user()
