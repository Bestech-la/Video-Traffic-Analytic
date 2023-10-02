from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


class TestUserSetup(APITestCase):
    def setUp(self) -> None:
        self.register_url = reverse('register_staff')
        self.auth_url = reverse('auth_register')
        self.login_url = reverse('token_obtain_pair')
        self.user_urls = reverse('user')
        self.user_url = reverse('user', kwargs={'pk': 2})
        self.url = reverse('auth_logout')

        self.testuser1 = User.objects.create_superuser(
            username='admin11', password='admin')

        self.client.login(username=self.testuser1.username,
                          password='admin') 

        self.user_data = {
                        'username': "med",
                        'password': "med",
                        'is_active': True,
                        'is_staff': True
                    }
        
        self.user_data_staff = {
                        'username': "med",
                        'password': "med",
                        'is_active': True,
                    }
        
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.refresh_token = self.get_refresh_token() 
    
    def get_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)
        return str(refresh)  