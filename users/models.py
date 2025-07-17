from django.contrib.auth.models import AbstractUser
from django.db import models

class Interest(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    interests = models.ManyToManyField(Interest, blank=True)

    def __str__(self):
        return self.username
