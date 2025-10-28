from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de usuários
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """
        Valida se as senhas coincidem
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs
    
    def validate_email(self, value):
        """
        Valida se o email já existe
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value
    
    def validate_username(self, value):
        """
        Valida se o username já existe
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value
    
    def create(self, validated_data):
        """
        Cria um novo usuário
        """
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer customizado para incluir mais dados no token JWT
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Adiciona claims customizadas
        token['username'] = user.username
        token['email'] = user.email
        # Adiciona roles do usuário
        token['roles'] = user.get_roles()
        
        return token


class UserLoginSerializer(CustomTokenObtainPairSerializer):
    """
    Serializer customizado para login com JWT
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
    
    def validate(self, attrs):
        """
        Valida as credenciais do usuário
        """
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Importante: como o USERNAME_FIELD do modelo é 'email',
            # devemos autenticar passando o email no parâmetro 'username'.
            # O ModelBackend usa USERNAME_FIELD internamente ao buscar o usuário.
            user = authenticate(username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Credenciais inválidas.')
            
            if not user.is_active:
                raise serializers.ValidationError('Conta desativada.')
            
            # Gera os tokens JWT
            refresh = self.get_token(user)
            attrs['refresh'] = str(refresh)
            attrs['access'] = str(refresh.access_token)
            attrs['user'] = user
            
            return attrs
        else:
            raise serializers.ValidationError('Email e senha são obrigatórios.')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para dados do usuário
    """
    full_name = serializers.ReadOnlyField()
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'is_active', 'date_joined', 'roles')
        read_only_fields = ('id', 'email', 'username', 'is_active', 'date_joined', 'roles')
    
    def get_roles(self, obj):
        """Retorna os roles do usuário"""
        return obj.get_roles()
    
    def update(self, instance, validated_data):
        """
        Atualiza os dados do usuário
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para alteração de senha
    """
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'},
        write_only=True
    )
    new_password_confirm = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, attrs):
        """
        Valida as senhas
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("As novas senhas não coincidem.")
        return attrs
    
    def validate_old_password(self, value):
        """
        Valida a senha atual
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value
