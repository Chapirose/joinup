from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet
from . import views

router = DefaultRouter()
router.register(r'', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('event/<int:event_id>/participate/', views.participate, name='participate_event'),
]