from rest_framework import serializers
from .models import Event, Participation, Group, Message
from users.serializers import UserSerializer

class EventSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source='creator.username', read_only=True)
    is_participating = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_is_participating(self, obj):
        user = self.context.get('request').user
        return user in obj.participants.all() if user.is_authenticated else False

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
