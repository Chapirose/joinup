from rest_framework import serializers
from .models import Event, Participation, Group, Message
from users.serializers import UserSerializer

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'creator']

    def validate(self, data):
        # Validation des données avant la sauvegarde
        if not data.get('title'):
            raise serializers.ValidationError("Le titre est requis.")
        if not data.get('description'):
            raise serializers.ValidationError("La description est requise.")
        if not data.get('date'):
            raise serializers.ValidationError("La date est requise.")
        if not data.get('location'):
            raise serializers.ValidationError("Le lieu est requis.")
        return data

class ParticipationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Participation
        fields = ['id', 'user', 'event', 'joined_at']

class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Group
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
