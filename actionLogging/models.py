from django.db import models
from datetime import datetime
from django.utils import timezone
import pytz




# class ActionLog(models.Model):
#     idLog = models.AutoField(primary_key=True)
#     idUser = models.CharField(max_length=100)
#     action = models.TextField()
#     timestamp = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return f"Log {self.idLog} - {self.idUser}"
class ActionLog(models.Model):
        
    id_user = models.CharField(max_length=100)
    log_created = models.DateTimeField(default=timezone.now)
    list_action = models.JSONField(default=list)

    def __str__(self):
        return self.id_user