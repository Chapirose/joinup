from django.db import models
from users.models import User  # important !
from django.conf import settings

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    participants = models.ManyToManyField(User, related_name='events_participated', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )

    def __str__(self):
        return f"{self.title} ({self.date.date()})"

class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} participates in {self.event.title}'

class Group(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='joinup_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Event: {self.event.title})"

class Message(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
