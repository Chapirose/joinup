from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from .models import Event
from .serializers import EventSerializer
from .models import Participation, Group, Message
from .serializers import ParticipationSerializer, GroupSerializer, MessageSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_detail.html', {'event': event})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def upcoming_events(request):
    user = request.user
    now_ = now()

    # Événements où l'utilisateur est participant
    participated_events = Event.objects.filter(participants=user, date__gte=now_).order_by('date')[:5]

    # Événements organisés par l'utilisateur
    created_events = Event.objects.filter(creator=user, date__gte=now_).order_by('date')[:5]

    return Response({
        "participated": EventSerializer(participated_events, many=True).data,
        "created": EventSerializer(created_events, many=True).data
    })

@login_required
def participate(request, event_id):
    # Récupère l'événement par ID
    event = Event.objects.get(id=event_id)

    # Essayer de créer la participation, ou si elle existe déjà, ne rien faire
    participation, created = Participation.objects.get_or_create(user=request.user, event=event)

    # Si l'utilisateur n'était pas encore inscrit, on le notifie
    if created:
        return JsonResponse({"message": "You have successfully joined the event."})
    else:
        return JsonResponse({"message": "You are already participating in this event."})

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, organizer=self.request.user)

    def get_queryset(self):
        # Ajoute un champ "is_participating" en annotation côté front
        return Event.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = EventSerializer(instance).data
        data["is_participating"] = request.user in instance.participants.all()
        data["creator_username"] = instance.creator.username
        return Response(data)

    @action(detail=True, methods=["post"])
    def participate(self, request, pk=None):
        try:
            event = self.get_object()
            event.participants.add(request.user)
            return Response({"detail": "Participation enregistrée."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ParticipationViewSet(viewsets.ModelViewSet):
    serializer_class = ParticipationSerializer
    queryset = Participation.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all().order_by('-date')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(creator=user, organizer=user)