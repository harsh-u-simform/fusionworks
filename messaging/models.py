from django.db import models

# Create your models here.

class ChatHistoryRecords(models.Model):
    data = models.BinaryField()
