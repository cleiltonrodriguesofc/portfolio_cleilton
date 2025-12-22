from rest_framework import serializers
from .models import Amostra, ActivityLog
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
        )


class AmostraSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    last_updated_by = UserSerializer(read_only=True)

    class Meta:
        model = Amostra
        fields = '__all__'
        read_only_fields = (
            'id_amostra',
            'data_criacao',
            'ultima_atualizacao',
            'peso_util',
            'status',
            'created_by',
            'last_updated_by',
        )


class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ActivityLog
        fields = '__all__'
        read_only_fields = (
            'timestamp',
            'user',
        )
