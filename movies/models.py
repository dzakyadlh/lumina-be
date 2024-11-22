from django.db import models

class Movies(models.Model):
    name = models.CharField(max_length=255)
    imageUrl = models.URLField(upload_to='movies/', blank=True, null=True)
    casts = models