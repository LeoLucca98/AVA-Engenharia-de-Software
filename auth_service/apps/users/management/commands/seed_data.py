from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria dados iniciais para o auth service (usuário admin)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove o usuário admin existente antes de criar',
        )

    def handle(self, *args, **options):
        self.stdout.write('Criando usuário admin...')
        
        admin_email = 'admin@ava.com'
        admin_username = 'admin'
        
        if options['reset']:
            # Remove o admin existente se existe (por email ou username)
            User.objects.filter(email=admin_email).delete()
            User.objects.filter(username=admin_username).delete()
            self.stdout.write('Usuário admin removido (se existia)')
        
        # Tenta buscar pelo email primeiro
        admin_user = User.objects.filter(email=admin_email).first()
        created = False
        
        if not admin_user:
            # Se não existe pelo email, verifica pelo username
            admin_user = User.objects.filter(username=admin_username).first()
        
        if not admin_user:
            # Cria novo usuário
            admin_user = User.objects.create_user(
                email=admin_email,
                username=admin_username,
                first_name='Administrador',
                last_name='Sistema',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            created = True
        else:
            # Atualiza dados se já existe
            admin_user.email = admin_email
            admin_user.username = admin_username
            admin_user.first_name = 'Administrador'
            admin_user.last_name = 'Sistema'
        
        # SEMPRE define a senha e permissões, mesmo se o usuário já existir
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Usuário admin criado com sucesso!\n'
                    f'  Email: {admin_email}\n'
                    f'  Senha: admin123'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'✓ Usuário admin atualizado com sucesso!\n'
                    f'  Email: {admin_email}\n'
                    f'  Senha: admin123 (atualizada)'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Seed do auth service concluído!')
        )
