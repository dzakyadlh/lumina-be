import requests
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import datetime
import hashlib
from django.conf import settings

class FetchMoviesView(APIView):
    base_url = 'https://moviesdatabase.p.rapidapi.com'
    cache_key_prefix = 'movies'
    def get(self, request):
        param = request.query_params.get('param','default')
        title_type = request.query_params.get('title_type', 'movie')
        genre = request.query_params.get('genre', None)
        title_search = request.query_params.get('title', None)
        movie_id = request.query_params.get('movie_id', None)
        page = request.query_params.get('page', 1)
        randomized = request.query_params.get('randomized', False)

        current_year = datetime.datetime.now().year

        # Randomized fetch
        if randomized:
            if title_type == 'movie':
                url = f"{self.base_url}/titles/random?limit=8&list=top_boxoffice_200"
                cache_key = self.generate_cache_key(title_type=title_type, page=page)
            else:
                url = f"{self.base_url}/titles/random?limit=8&list=most_pop_series"
                cache_key = self.generate_cache_key(title_type=title_type, page=page)
            data= cache.get(cache_key)
            if not data:
                data = self.process_movies(url)
                if data is None:
                    return Response(
                        {'message': 'Movies not found',},
                        status=status.HTTP_404_NOT_FOUND
                    )
                cache.set(cache_key, data)
            return Response({'message':'Movies data fetched', 'data':data,}, status=status.HTTP_200_OK)
        
        if title_search:
            cache_key = self.generate_cache_key(title_search=title_search, page=page)
            data = cache.get(cache_key)
            if not data:
                url1 = f"{self.base_url}/titles/search/title/{title_search}?exact=false&titleType=movie"
                url2 = f"{self.base_url}/titles/search/title/{title_search}?exact=false&titleType=tvSeries"
                data = self.process_movies(url1) + self.process_movies(url2)
                if data is None:
                    return Response(
                        {'message': 'Movies not found',},
                        status=status.HTTP_404_NOT_FOUND
                    )
                cache.set(cache_key, data)
            return Response({'message':'Movies data fetched', 'data':data,}, status=status.HTTP_200_OK)

        # Cache key customization
        if movie_id:
            cache_key = self.generate_cache_key(movie_id=movie_id)
        else:
            cache_key = self.generate_cache_key(param=param, title_type=title_type, genre=genre, title_search=title_search, page=page)

        # Get cache if exists
        data = cache.get(cache_key)

        # If cache is not exists
        if not data:
            try:
                url = self.base_url

                if movie_id:
                    url = f"{url}/titles/{movie_id}?info=base_info"
                    data = self.process_movie(url)
                else:
                    if title_type == 'tvSeries':
                        url = f"{self.base_url}/titles/random"
                    else:
                        url = f"{self.base_url}/titles"
                    query_params = {
                        "endYear": current_year,
                        "page": page,
                        "titleType": title_type,
                        "sort": "year.incr" if title_search else None,
                        "list": self.get_list_type(param, title_type),
                        "limit": 8,
                        "info": "base_info" if param == "trending" else None,
                    }
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
        headers = {'X-RapidAPI-Key': settings.RAPIDAPI_KEY,'X-RapidAPI-Host': 'moviesdatabase.p.rapidapi.com'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        movie = response.json().get('results', {})
        data = {
            "movie_id": movie.get("id", None),
            "title": movie.get("titleText", {}).get("text", "Unknown Title"),
            "imageUrl": movie.get("primaryImage").get("url") if movie.get("primaryImage") else None,
            "releaseYear": movie.get("releaseYear", {}).get("year", None) if movie.get("releaseYear") else None,
            "plot": movie.get("plot", {}).get("plotText", {}).get("plainText", None) if movie.get("plot") else None,
            "genres": movie.get("genres", {}).get("genres", []) if movie.get("genres") else None,
            "stars": movie.get("primaryImage", {}).get("caption", {}).get("plainText", None) if movie.get("primaryImage") else None,
            "rating":movie.get("ratingsSummary", {}).get("aggregateRating", None) if movie.get("ratingsSummary") else None,
            "runtime":movie.get("runtime", {}).get("seconds", None) if movie.get("runtime") else None,
            "episodes":movie.get("episodes", {}) if movie.get("episodes") else None,
        }
        return data
    
    def process_movies(self, url):
        headers = {'X-RapidAPI-Key':settings.RAPIDAPI_KEY,'X-RapidAPI-Host': 'moviesdatabase.p.rapidapi.com'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        movies_data = response.json().get('results', [])
        print(url)
        data = []

        for movie in movies_data:
            data.append({
                "movie_id": movie.get("id", None),
                "title": movie.get("titleText", {}).get("text", "Unknown Title"),
                "imageUrl": movie.get("primaryImage").get("url") if movie.get("primaryImage") else None,
                "releaseYear": movie.get("releaseYear", {}).get("year", None) if movie.get("releaseYear") else None,
                "is_series": movie.get("titleType", {}).get("isSeries", False),
                "plot": movie.get("plot", {}).get("plotText", {}).get("plainText", None) if movie.get("plot") else None,
            })

        return data
    
    def build_query_string(self, params):
        # Helper method to construct query string
        return "?" + "&".join([f"{key}={value}" for key, value in params.items() if value])

    def get_list_type(self, param, title_type):
        # Map `param` to specific API lists
        lists = {
            "default": None if title_type == 'movie' else 'most_pop_series',
            "trending": "top_boxoffice_last_weekend_10",
            "popular": "top_boxoffice_200",
            "popularSeries": "top_rated_series_250"
        }
        return lists.get(param, None)
    
    def generate_cache_key(self, **kwargs):
        raw_key = f"{self.cache_key_prefix}:{kwargs}"
        return hashlib.md5(raw_key.encode()).hexdigest()
        