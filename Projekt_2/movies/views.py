from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import OpenApiParameter
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Movie, Review
from .serializers import MovieSerializer, MovieListSerializer, ReviewSerializer
from .services import TMDBService

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['language', 'genres']
    search_fields = ['title', 'description']
    ordering_fields = ['release_date', 'rating']
    ordering = ['-release_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return MovieListSerializer
        return MovieSerializer
    
    # == Pobierz popularne filmy z TMDB ==
    @action(detail=False, methods=['post'])
    def fetch_trending(self, request):
        service = TMDBService()
        movies = service.fetch_trending_movies()
        return Response({
            'count': len(movies),
            'message': f'Pobrano {len(movies)} filmów'
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='q',
                description='Fraza wyszukania',
                required=True,
                location=OpenApiParameter.QUERY,
            )
        ]
    )
    # == Wyszukaj film w TMDB ==
    @action(detail=False, methods=['get'])
    def search_tmdb(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'Parametr q jest wymagany'},
                status=status.HTTP_400_BAD_REQUEST
            )
        service = TMDBService()
        results = service.search_movies(query)
        return Response(results)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'

    def get_queryset(self):
        movie_id = self.kwargs.get('movie_pk')
        return Review.objects.filter(movie_id=movie_id)
    
    def perform_create(self, serializer):
        movie_id = self.kwargs.get('movie_pk')
        movie = Movie.objects.get(id=movie_id)
        serializer.save(user=self.request.user, movie=movie)