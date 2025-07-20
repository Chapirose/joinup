from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from .serializers import RegisterSerializer

User = get_user_model()

class UserViewSet(viewsets.ReadOnlyModelViewSet):  # pas d'édition pour le moment
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]