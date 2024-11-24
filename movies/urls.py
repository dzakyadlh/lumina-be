from django.urls import path
from .views import FetchMoviesView

urlpatterns = [
    path('api/movies/', FetchMoviesView.as_view(), name='fetch-movies'),
]
