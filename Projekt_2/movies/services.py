import requests
from django.conf import settings
from .models import Movie
from django.utils.dateparse import parse_date

class TMDBService:
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL

    def fetch_trending_movies(self, time_window='week'):
        url = f"{self.base_url}/trending/movie/{time_window}"
        params = {'api_key': self.api_key, 'language': 'pl-PL'}

        response = requests.get(url, params=params)
        response.raise_for_status()

        movies_data = response.json().get('results', [])
        created_movies = []

        for movie_data in movies_data:
            movie, created = Movie.objects.get_or_create(
                tmdb_id=movie_data['id'],
                defaults={
                    'title': movie_data.get('title', ''),
                    'description': movie_data.get('overview', ''),
                    'release_date': parse_date(movie_data.get('release_date', '')),
                    'rating': movie_data.get('vote_average', 0.0),
                    'poster_url': f"https://image.tmdb.org/t/w342{movie_data.get('poster_path', '')}",
                    'backdrop_url': f"https://image.tmdb.org/t/p/w780{movie_data.get('backdrop_path', '')}",
                    'language': 'pl',
                }
            )
            if created:
                created_movies.append(movie)

        return created_movies
    
    def search_movies(self, query, language='pl-PL'):
        url = f"{self.base_url}/search/movie"
        params = {
            'api_key': self.api_key,
            'query': query,
            'language': language,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        return response.json()
    
    def get_movie_details(self, tmdb_id):
        url = f"{self.base_url}/movie/{tmdb_id}"
        params = {'api_key': self.api_key, 'language': 'pl-PL'}

        response = requests.get(url, params=params)
        response.raise_for_status()

        return response.json()