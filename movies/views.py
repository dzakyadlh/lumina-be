import requests
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Movies
from .serializers import MoviesSerializer
import datetime

class FetchMoviesView(APIView):
    base_url = 'https://moviesdatabase.p.rapidapi.com'
    cache_key_prefix = 'movies'
    def get(self, request):
        param = request.query_params.get('param','latest')
        title_type = request.query_params.get('title_type', None)
        genre = request.query_params.get('genre', None)
        title_search = request.query_params.get('title', None)
        movie_id = request.query_params.get('movie_id', None)
        page = request.query_params.get('page', 1)

        current_year = datetime.datetime.now().year
        if movie_id:
            cache_key = f"{self.cache_key_prefix}:{movie_id}"
        else:
            cache_key = f"{self.cache_key_prefix}:{param}:{title_type or 'all'}:{genre or 'all'}:{title_search or 'all'}:{page}"
        data = cache.get(cache_key)

        if not data:
            try:
                url = self.base_url

                if movie_id:
                    url = f"{url}/titles/{movie_id}?info=base_info"
                    data = self.process_movie(url)
                else:
                    url = f"{self.base_url}/titles"
                    query_params = {
                        "endYear": current_year,
                        "page": page,
                        "titleType": title_type if title_type else "movie",
                        "sort": "year.incr" if title_search else None,
                        "list": self.get_list_type(param),
                    }
                    # Add filters
                    if title_search:
                        url = f"{self.base_url}/titles/search/title/{title_search}?exact=false&info=base_info"
                    if genre:
                        query_params["genre"] = genre
                    
                    # Append query parameters
                    url += self.build_query_string(query_params)
                    data = self.process_movies(url)
                if data is None:
                    return Response(
                        {'message': 'Movies not found',},
                        status=status.HTTP_404_NOT_FOUND
                    )
                cache.set(cache_key, data)

            except requests.exceptions.RequestException as e:
                return Response(
                    {'message': 'Fetching movies data failed', 'error':str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response({'message':'Movies data fetched', 'data':data,}, status=status.HTTP_200_OK)
    
    def process_movie(self, url):
        headers = {'X-RapidAPI-Key':'5f86fd7d25msh82389c264fed047p12a461jsn31581c0b17f1','X-RapidAPI-Host': 'moviesdatabase.p.rapidapi.com'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get('results', {})
        return data
    
    def process_movies(self, url):
        headers = {'X-RapidAPI-Key':'5f86fd7d25msh82389c264fed047p12a461jsn31581c0b17f1','X-RapidAPI-Host': 'moviesdatabase.p.rapidapi.com'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        movies_data = response.json().get('results', [])
        data = []

        for movie in movies_data:
            data.append({
                "movie_id": movie.get("id", None),
                "title": movie.get("titleText", {}).get("text", "Unknown Title"),
                "imageUrl": movie.get("primaryImage").get("url") if movie.get("primaryImage") else None,
                "releaseYear": movie.get("releaseYear", {}).get("year", None),
                "category": movie.get("titleType", {}).get("categories", [{}])[0].get("value", "Unknown Category"),
                "is_series": movie.get("titleType", {}).get("isSeries", False),
            })

        return data
    
    def build_query_string(self, params):
        # Helper method to construct query string
        return "?" + "&".join([f"{key}={value}" for key, value in params.items() if value])

    def get_list_type(self, param):
        # Map `param` to specific API lists
        lists = {
            "latest": None,
            "trending": "top_boxoffice_last_weekend_10",
            "popular": "top_boxoffice_200",
        }
        return lists.get(param, None)
        