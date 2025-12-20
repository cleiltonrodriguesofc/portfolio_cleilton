from django.apps import AppConfig

class PrograosConfig(AppConfig): # Class name can be different
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prograos' # Coloque o nome do seu app aqui

    def ready(self):
        import prograos.signals # Importa os sinais