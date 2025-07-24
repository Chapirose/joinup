from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, CreateEventView, DeleteEvent, ParticipateEvent, UnparticipateEvent
from . import views

router = DefaultRouter()
router.register(r'', EventViewSet, basename='event')

urlpatterns = [
    path('create/', views.CreateEventView.as_view(), name='create_event'),
    path('', include(router.urls)),
    path('event/<int:event_id>/participate/', views.participate, name='participate_event'),
    path('my-created/', views.my_created_events, name='my_created_events'),
    path('my-participations/', views.my_participated_events, name='my_participated_events'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/my-events/', views.my_events, name='my-events'),
    path('events/<int:pk>/', DeleteEvent.as_view(), name='delete-event'),
     path('events/<int:pk>/participate/', ParticipateEvent.as_view(), name='participate-event'),
    path('events/<int:pk>/unparticipate/', UnparticipateEvent.as_view(), name='unparticipate-event'),
]