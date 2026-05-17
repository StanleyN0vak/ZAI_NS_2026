from rest_framework import serializers
from .models import Favorite
from movies.serializers import MovieListSerializer

class FavoriteSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'movie', 'movie_id', 'added_at']
        read_only_fields = ['added_at']

    def create(self, validated_data):
        movie_id = validated_data.pop('movie_id')
        from movies.models import Movie
        movie = Movie.objects.get(id=movie_id)
        user = self.context['request'].user
        return Favorite.objects.create(movie=movie, user=user) 