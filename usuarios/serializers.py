from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "nome", "email", "foto"]  # não exponha senha

class UsuarioCreateSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "nome", "email", "senha", "foto"]

    def validate_senha(self, senha):
        erros = []
        if not senha or len(senha) < 8:
            erros.append("A senha deve ter pelo menos 8 caracteres.")
        if not any(c.isdigit() for c in senha):
            erros.append("A senha deve ter pelo menos um número.")
        if not any(c.isalpha() for c in senha):
            erros.append("A senha deve ter pelo menos uma letra.")
        if not any(c.isupper() for c in senha):
            erros.append("A senha deve ter pelo menos uma letra maiúscula.")
        if not any(c.islower() for c in senha):
            erros.append("A senha deve ter pelo menos uma letra minúscula.")
        if not any(not c.isalnum() for c in senha):
            erros.append("A senha deve ter pelo menos um caractere especial.")
        if erros:
            raise serializers.ValidationError(erros)
        return senha

    def create(self, validated_data):
        senha = validated_data.pop("senha")
        validated_data["senha"] = make_password(senha)  # hash seguro
        return super().create(validated_data)

class AlterarSenhaSerializer(serializers.Serializer):
    senha = serializers.CharField(write_only=True)

    def validate_senha(self, senha):
        # mesma validação
        if not senha or len(senha) < 8:
            raise serializers.ValidationError("A senha deve ter pelo menos 8 caracteres.")
        if not any(c.isdigit() for c in senha):
            raise serializers.ValidationError("A senha deve ter pelo menos um número.")
        if not any(c.isalpha() for c in senha):
            raise serializers.ValidationError("A senha deve ter pelo menos uma letra.")
        if not any(c.isupper() for c in senha):
            raise serializers.ValidationError("A senha deve ter pelo menos uma letra maiúscula.")
        if not any(c.islower() for c in senha):
            raise serializers.ValidationError("A senha deve ter pelo menos uma letra minúscula.")
        if not any(not c.isalnum() for c in senha):
            raise serializers.ValidationError("A senha deve ter pelo menos um caractere especial.")
        return senha
