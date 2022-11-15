from django.core.exceptions import ValidationError
import json

from django.db import models
from django.utils.translation import gettext_lazy
import datetime
# Create your models here.

def validate_stopping_point(value):
    try:
        stopping = json.loads(value)
        for itm in stopping:
            if 'name' in itm and 'lat' in itm and 'lon' in itm:
                continue
            else:
                raise ValidationError('ERROR')
    except BaseException:
        raise ValidationError('Not exists nursery field')


def validate_route_type(value):
    if value.title() not in ["Car", "Foot"]:
        raise ValidationError('ERROR')


def validate_date(value):
    # try:
    #     parse_date = datetime.strptime(str(value), "%Y-%m-%d")
    # except BaseException:
    #     raise ValidationError('ERROR date format')

    if datetime.date.today() > value:
        raise ValidationError('ERROR date should be in future')


class Places(models.Model):
    name = models.CharField(max_length=50)


class Route(models.Model):
    class RouteType(models.TextChoices):
        car = 'car', gettext_lazy('car')
        foot = 'foot', gettext_lazy('foot')
        bicycle = 'bicycle', gettext_lazy('bicycle')

    start_point = models.IntegerField()
    stopping_point = models.CharField(max_length=50)
    destination = models.IntegerField()
    country = models.CharField(max_length=50)
    location = models.CharField(max_length=120)
    description = models.TextField()
    route_type = models.CharField(max_length=10, choices=RouteType.choices, default=RouteType.foot,
                                  validators=[validate_route_type])
    duration = models.IntegerField()


class Review(models.Model):
    route_id = models.IntegerField()
    review = models.TextField()
    review_rate = models.IntegerField()


class Event(models.Model):
    id_route = models.IntegerField()
    event_admin = models.IntegerField()
    event_users = models.CharField(max_length=50, null=True)
    start_date = models.DateField(validators=[validate_date])
    price = models.IntegerField()
