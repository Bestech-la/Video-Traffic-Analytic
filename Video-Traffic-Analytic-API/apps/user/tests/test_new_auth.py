from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken


class LoginTestCaseNewAuth(APITestCase):
    def setUp(self):
        self.url = reverse('rest_login')
        self.url_logout = reverse('rest_logout')
        self.url_change = reverse('rest_password_change')
        self.url_reset = reverse('rest_password_reset')
        self.url_confirm = reverse('rest_password_reset_confirm')
        self.url_refresh = '/api/v1/auth/token/refresh/'
        self.blacklist_url = reverse('token_blacklist')
        self.url_user_detail = reverse('rest_user_details')
        self.username = 'testuser'
        self.email = 'test@example.com'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.token = Token.objects.create(user=self.user)

        self.testuser1 = User.objects.create_superuser(
            username='user', password='admin')

        self.client.login(username=self.testuser1.username,
                          password='admin')
        self.token = self.get_token()
        self.refresh_token = self.get_refresh_token()
    def get_token(self):
        refresh = RefreshToken.for_user(self.user)
        return str(refresh.access_token)  
    
    def get_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)
        return str(refresh) 
    
    

    def test_login_with_valid_credentials(self):
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        token = response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.get(self.url_user_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pk'], self.user.pk)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)

    def test_login_with_invalid_credentials(self):
        data = {
            'username': self.username,
            'password': 'wrongpassword'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_logout(self):
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(self.url, data)
        token = response.data['access_token']
        token = response.data['refresh_token']

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        data = {
            "refresh": self.refresh_token
        }
        response = self.client.post(self.url_logout, data)
        print("=====response.data_logout===", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Successfully logged out.')
        self.client.credentials

    def test_change_password_with_valid_credentials(self):
        data = {
            'new_password1': 'newtestpassword',
            'new_password2': 'newtestpassword',
            'old_password': self.password
        }
        response = self.client.post(self.url_change, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.user.refresh_from_db()

    def test_change_password_with_invalid_credentials(self):
        data = {
            'new_password1': 'newtestpassword',
            'new_password2': 'newtestpassword2', 
            'old_password': self.password
        }
        response = self.client.post(self.url_change, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))


    def test_refresh_token_with_valid_token(self):

        self.testuser1 = User.objects.create_superuser(
            username='user1', password='admin')

        self.client.login(username=self.testuser1.username,
                          password='admin')
        data = {
            "refresh": self.refresh_token
        }
        response = self.client.post(self.url_refresh, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('access_token_expiration', response.data)


    def test_verify_token(self):
        verify_url = '/api/v1/auth/token/verify/'
        self.testuser1 = User.objects.create_superuser(
            username='user1', password='admin')
        self.client.login(username=self.testuser1.username,
                          password='admin')
        data = {
            "token": self.token
        }
        response = self.client.post(verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_invalid_token(self):
        verify_url = '/api/v1/auth/token/verify/'
        self.testuser1 = User.objects.create_superuser(
            username='user1', password='admin')
        self.client.login(username=self.testuser1.username,
                          password='admin')
        data = {
            "token": "Wrong Token"
            }
        response = self.client.post(verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_blacklist_token(self):
        data = {
            "refresh": self.refresh_token
        }
        response = self.client.post(self.blacklist_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_blacklist_token(self):
        data = {
            "refresh": "Wrong Refresh"
        }
        response = self.client.post(self.blacklist_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)