from __future__ import absolute_import, unicode_literals
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import shared_task
from django.db.models import Q, Count
from .models import *
import datetime
from django.core.exceptions import ObjectDoesNotExist
from library import models as librarymodels

from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@shared_task
def owner_subscription_checker():
    owners = Owner.objects.all()

    for owner in owners:
        
        if owner.active_subscription is None:
            pass
        else:
            activeSub = OwnerSubscriptionPlan.objects.get(id=owner.active_subscription.id)
            print(activeSub)

            if (activeSub.enddate - datetime.date.today()).days <0:
                activeSub.active = False
                
                activeSub.save()
                ownerobj = Owner.objects.get(id=owner.id)
                ownerobj.active_subscription = None
                ownerobj.save()
                activeSub.save()