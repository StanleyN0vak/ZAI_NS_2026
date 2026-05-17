from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from movies.models import Movie
from .models import Favorite

class FavoriteAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='favuser',
            password='favpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        
        self.movie1 = Movie.objects.create(
            tmdb_id=200,
            title='Favorite Movie 1',
            rating=9.0
        )
        
        self.movie2 = Movie.objects.create(
            tmdb_id=201,
            title='Favorite Movie 2',
            rating=8.5
        )
        
        self.favorite = Favorite.objects.create(
            user=self.user,
            movie=self.movie1
        )

    # === GET Tests ===
    def test_get_favorites_authenticated(self):
        """Test getting user's favorites"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/favorites/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_get_favorite_detail(self):
        """Test getting specific favorite"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/favorites/{self.favorite.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['movie']['id'], self.movie1.id)

    # === POST Tests ===
    def test_add_favorite_authenticated(self):
        """Test adding movie to favorites"""
        self.client.force_authenticate(user=self.user)
        data = {'movie_id': self.movie2.id}
        response = self.client.post('/api/favorites/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_favorite_unauthenticated(self):
        """Test adding favorite without authentication"""
        data = {'movie': self.movie2.id}
        response = self.client.post('/api/favorites/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # === PUT/PATCH Tests ===
    def test_update_favorite_authenticated(self):
        """Test updating favorite"""
        self.client.force_authenticate(user=self.user)
        data = {'movie': self.movie2.id}
        response = self.client.patch(f'/api/favorites/{self.favorite.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_favorite_other_user(self):
        """Test updating other user's favorite (should fail)"""
        self.client.force_authenticate(user=self.other_user)
        data = {'movie': self.movie2.id}
        response = self.client.patch(f'/api/favorites/{self.favorite.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # === DELETE Tests ===
    def test_delete_favorite_authenticated(self):
        """Test removing favorite"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/favorites/{self.favorite.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_favorite_unauthenticated(self):
        """Test removing favorite without authentication"""
        response = self.client.delete(f'/api/favorites/{self.favorite.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)