from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User

class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='authuser',
            password='authpass123'
        )

    # === Token Obtain Tests ===
    def test_obtain_token_valid_credentials(self):
        """Test obtaining JWT token with valid credentials"""
        data = {
            'username': 'authuser',
            'password': 'authpass123'
        }
        response = self.client.post('/api/token/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_invalid_credentials(self):
        """Test obtaining token with invalid password"""
        data = {
            'username': 'authuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/token/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # === Token Refresh Tests ===
    def test_refresh_token(self):
        """Test refreshing JWT token"""
        # First get the token
        obtain_data = {
            'username': 'authuser',
            'password': 'authpass123'
        }
        obtain_response = self.client.post('/api/token/', obtain_data)
        refresh_token = obtain_response.data['refresh']
        
        # Now refresh it
        refresh_data = {'refresh': refresh_token}
        response = self.client.post('/api/token/refresh/', refresh_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_token_invalid(self):
        """Test refreshing with invalid token"""
        data = {'refresh': 'invalid_token'}
        response = self.client.post('/api/token/refresh/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # === Protected Endpoints Tests ===
    def test_access_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token"""
        # Get token
        obtain_data = {
            'username': 'authuser',
            'password': 'authpass123'
        }
        obtain_response = self.client.post('/api/token/', obtain_data)
        access_token = obtain_response.data['access']
        
        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/favorites/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = self.client.get('/api/favorites/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)