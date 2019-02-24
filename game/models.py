from django.db import models


# Create your core here.
class User(models.Model):
    name = models.TextField(null=False, blank=False)
    key = models.TextField(null=False, blank=False, unique=True)


class Job(models.Model):
    name = models.TextField(null=False, blank=False)


class Room(models.Model):
    name = models.TextField()
    users = models.ManyToManyField(User)
    jobs = models.ManyToManyField(Job)

