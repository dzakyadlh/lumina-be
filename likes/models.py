from django.db import models
from ..users import models

class Likes(models.Model):
    user_id = models.ForeignKey(models.CustomUser)
    liked_movies_id = models.JSONField(default=list, blank=True)
