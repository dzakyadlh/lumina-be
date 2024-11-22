from django.db import models
from users.models import CustomUser

class Likes(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    liked_movie_ids = models.JSONField(default=list, blank=True)  # Store movie IDs in JSONField

    def __str__(self):
        return f"{self.user_id.username}'s likes"
