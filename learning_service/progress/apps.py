from django.apps import AppConfig


class ProgressConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Corrige o caminho do app para refletir a estrutura real (learning_service/progress)
    name = 'progress'
    verbose_name = 'Progresso'
