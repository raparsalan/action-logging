from django.db import models
from datetime import datetime
from django.utils import timezone
import pytz


class ActionLog(models.Model):
    idLog = models.AutoField(primary_key=True)
    id_user = models.CharField(max_length=100)
    log_created = models.DateTimeField(default=timezone.now)
    list_action = models.JSONField(default=list)

    def __str__(self):
        return self.id_user