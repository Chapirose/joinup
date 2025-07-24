from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from .models import Participation, Group, Message, Event
from .serializers import ParticipationSerializer, GroupSerializer, MessageSerializer, EventSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView

class EventCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Assigner l'utilisateur à 'creator' à partir de l'utilisateur authentifié
        data = request.data
        data['creator'] = request.user.id  # Récupère l'ID de l'utilisateur authentifié

        serializer = EventSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all().order_by('-date')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(creator=user, organizer=user)

class CreateEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ParticipateEvent(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user
        if Participation.objects.filter(event=event, user=user).exists():
            return Response({"detail": "Vous êtes déjà inscrit à cet événement."}, status=status.HTTP_400_BAD_REQUEST)

        participation = Participation.objects.create(event=event, user=user)
        return Response({"detail": "Inscription réussie."}, status=status.HTTP_201_CREATED)

class UnparticipateEvent(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user
        participation = Participation.objects.filter(event=event, user=user)

        if not participation.exists():
            return Response({"detail": "Vous n'êtes pas inscrit à cet événement."}, status=status.HTTP_400_BAD_REQUEST)

        participation.delete()
        return Response({"detail": "Désinscription réussie."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def create_event(request):
    if request.method == 'POST':
        serializer = EventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()  # Sauvegarder avec l'utilisateur associé
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

@login_required
def my_created_events(request):
    # Récupère tous les événements créés par l'utilisateur connecté
    events = Event.objects.filter(creator=request.user)
    event_data = [{
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'date': event.date,
        'location': event.location,
        'creator_username': event.creator.username
    } for event in events]

    return JsonResponse({'events': event_data})

@login_required
def my_participated_events(request):
    # Récupère tous les événements auxquels l'utilisateur est inscrit
    participations = Participation.objects.filter(user=request.user)
    event_ids = [participation.event.id for participation in participations]
    events = Event.objects.filter(id__in=event_ids)
    event_data = [{
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'date': event.date,
        'location': event.location,
        'creator_username': event.creator.username
    } for event in events]

    return JsonResponse({'events': event_data})

def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_events(request):
    events = Event.objects.filter(creator=request.user)  # Récupère les événements créés par l'utilisateur connecté
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

class DeleteEvent(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            event = Event.objects.get(pk=pk, creator=request.user)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            return Response({"detail": "Événement non trouvé ou vous n'êtes pas le créateur."}, status=status.HTTP_404_NOT_FOUND)