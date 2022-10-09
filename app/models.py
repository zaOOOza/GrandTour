from django.db import models
from django.utils.translation import gettext_lazy
from django.utils import timezone


# Create your models here.


class Places(models.Model):
    name = models.CharField(max_length=50)


class Route(models.Model):
    class RouteType(models.TextChoices):
        car = 'car', gettext_lazy('car')
        foot = 'foot', gettext_lazy('foot')
        bicycle = 'bicycle', gettext_lazy('bicycle')

    start_point = models.IntegerField()
    stopping_point = models.JSONField()
    destination = models.IntegerField()
    country = models.CharField(max_length=50)
    location = models.CharField(max_length=120)
    description = models.TextField()
    route_type = models.CharField(max_length=10, choices=RouteType.choices, default=RouteType.foot)
    duration = models.IntegerField()


class Review(models.Model):
    route_id = models.IntegerField()
    review = models.TextField()
    review_rate = models.IntegerField()


class Event(models.Model):
    id_route = models.IntegerField()
    event_admin = models.IntegerField()
    approved_user = models.JSONField()
    pending_user = models.JSONField()
    start_date = models.TextField(default=timezone.now)
    price = models.IntegerField()



