from rest_framework import serializers
from .models import Likes

class LikesSerializer(serializers.ModelSerializer):
    liked_movie_ids = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Likes
        fields = ['user_id', 'liked_movie_ids']