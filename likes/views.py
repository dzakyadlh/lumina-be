from rest_framework import status, viewsets
from rest_framework.response import Response
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from .serializers import LikesSerializer
from .models import Likes

class LikesViewSet(viewsets.ModelViewSet):
    serializer_class = LikesSerializer
    queryset = Likes.objects.all()
    permission_classes = [IsAuthenticated]

    def get_cache_key(self, user_id):
        return f"likes:{user_id}"

    def list(self, request, *args, **kwargs):
        """
        Handles listing all likes. Cached for faster responses.
        """
        user_id = request.user.id
        cache_key = self.get_cache_key(user_id)
        data = cache.get(cache_key)

        if not data:
            likes_instance, created = Likes.objects.get_or_create(user_id=request.user)
            serializer = self.get_serializer(likes_instance)
            data = serializer.data
            cache.set(cache_key, data)

        return Response(
            {'message': 'Fetch success', 'data': data},
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        """
        Handles updating a likes instance.
        Clears the cache to ensure data consistency.
        """
        user_id = request.user.id
        cache_key = self.get_cache_key(user_id)
        cache.delete(cache_key)

        likes, created = Likes.objects.get_or_create(user_id=request.user)
        # Get the movie ID from the request
        movie_id = request.data.get('movie_id')
        if not movie_id:
            return Response(
                {'message': 'Movie ID is required to add a liked movie.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if movie_id not in likes.liked_movie_ids:
            likes.liked_movie_ids.append(movie_id)
            likes.save()

        cache.delete(cache_key)
        cache.set(cache_key, LikesSerializer(likes).data)
        
        return Response(
            {'message': 'Added liked movie', 'data': LikesSerializer(likes).data},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        """
        Handles deleting a liked movie by its movie_id.
        Clears the cache to ensure data consistency.
        """
        user_id = request.user.id
        cache_key = self.get_cache_key(user_id)
        cache.delete(cache_key)
        
        # Get the user-related 'Likes' instance
        likes = self.get_object()
        
        # Get movie_id from request data (expected as an integer ID)
        movie_id = request.data.get('movie_id')

        if not movie_id:
            return Response(
                {'message': 'Movie ID is required to remove a liked movie.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove the movie ID from the liked_movies list (it's just an ID now)
        if movie_id in likes.liked_movie_ids:
            likes.liked_movie_ids.remove(movie_id)
            likes.save()

            # Clear cache for user-related data
            cache.delete(cache_key)
            cache.set(cache_key, LikesSerializer(likes).data)

            return Response(
                {'message': 'Removed movie from liked movies', 'data':LikesSerializer(likes).data},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'message': 'Movie ID not found in liked movies list.'},
            status=status.HTTP_404_NOT_FOUND
        )

