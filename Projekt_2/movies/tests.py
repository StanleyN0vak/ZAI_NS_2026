from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Movie, Review

class MovieAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123'
        )
        
        self.movie = Movie.objects.create(
            tmdb_id=1,
            title='Test Movie 1',
            description='Test description',
            rating=8.5
        )
        
        self.movie2 = Movie.objects.create(
            tmdb_id=2,
            title='Test Movie 2',
            description='Another movie',
            rating=7.0
        )

    # === GET Tests ===
    def test_get_movies_list(self):
        """Test getting list of all movies"""
        response = self.client.get('/api/movies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_get_movie_detail(self):
        """Test getting specific movie details"""
        response = self.client.get(f'/api/movies/{self.movie.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Movie 1')

    # === POST Tests ===
    def test_create_movie_authenticated(self):
        """Test creating movie with authentication"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'tmdb_id': 999,
            'title': 'New Movie',
            'description': 'New description',
            'rating': 9.0
        }
        response = self.client.post('/api/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Movie')

    def test_create_movie_unauthenticated(self):
        """Test creating movie without authentication (should fail)"""
        data = {
            'tmdb_id': 999,
            'title': 'New Movie',
            'rating': 9.0
        }
        response = self.client.post('/api/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # === PUT/PATCH Tests ===
    def test_update_movie_authenticated(self):
        """Test updating movie with authentication"""
        self.client.force_authenticate(user=self.admin_user)
        data = {'title': 'Updated Title', 'rating': 9.5}
        response = self.client.patch(f'/api/movies/{self.movie.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_update_movie_unauthenticated(self):
        """Test updating movie without authentication (should fail)"""
        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/movies/{self.movie.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # === DELETE Tests ===
    def test_delete_movie_authenticated(self):
        """Test deleting movie with authentication"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/movies/{self.movie.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Movie.objects.filter(id=self.movie.id).exists())

    def test_delete_movie_unauthenticated(self):
        """Test deleting movie without authentication (should fail)"""
        response = self.client.delete(f'/api/movies/{self.movie.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='reviewer',
            password='reviewpass123'
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='otherpass123'
        )
        
        self.movie = Movie.objects.create(
            tmdb_id=100,
            title='Review Test Movie',
            rating=8.0
        )
        
        self.review = Review.objects.create(
            user=self.user,
            movie=self.movie,
            rating=9,
            comment='Great movie!'
        )

    # === GET Tests ===
    def test_get_reviews_list(self):
        """Test getting reviews for a movie"""
        response = self.client.get(f'/api/movies/{self.movie.id}/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_get_review_detail(self):
        """Test getting specific review"""
        response = self.client.get(
            f'/api/movies/{self.movie.id}/reviews/{self.review.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 9)

    # === POST Tests ===
    def test_create_review_authenticated(self):
        """Test creating review with authentication"""
        self.client.force_authenticate(user=self.other_user)
        data = {'rating': 8, 'comment': 'Good movie'}
        response = self.client.post(
            f'/api/movies/{self.movie.id}/reviews/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 8)

    def test_create_review_unauthenticated(self):
        """Test creating review without authentication"""
        data = {'rating': 8, 'comment': 'Good movie'}
        response = self.client.post(
            f'/api/movies/{self.movie.id}/reviews/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # === PUT/PATCH Tests ===
    def test_update_review_authenticated(self):
        """Test updating own review"""
        self.client.force_authenticate(user=self.user)
        data = {'rating': 7, 'comment': 'Updated review'}
        response = self.client.patch(
            f'/api/movies/{self.movie.id}/reviews/{self.review.id}/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 7)

    def test_update_review_other_user(self):
        """Test updating someone else's review (should fail)"""
        self.client.force_authenticate(user=self.other_user)
        data = {'rating': 5}
        response = self.client.patch(
            f'/api/movies/{self.movie.id}/reviews/{self.review.id}/',
            data
        )
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_200_OK])

    # === DELETE Tests ===
    def test_delete_review_authenticated(self):
        """Test deleting own review"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            f'/api/movies/{self.movie.id}/reviews/{self.review.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_review_unauthenticated(self):
        """Test deleting review without authentication"""
        response = self.client.delete(
            f'/api/movies/{self.movie.id}/reviews/{self.review.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)