from .test_user_setup import TestUserSetup
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse

class AuthTestCase(TestUserSetup):    
    
    def test_register_no_data(self):
        res = self.client.post(self.register_url, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_data(self):
        res = self.client.post(
            self.register_url, self.user_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_register_with_staff(self):
        res = self.client.post(
            self.auth_url, self.user_data_staff, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_login(self):
        self.client.post(self.register_url, self.user_data, format="json")
        res = self.client.post(self.login_url, self.user_data, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_get_all_user(self):
        res = self.client.get(self.user_urls)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data['count'], int)
        self.assertEqual(res.data['count'],2)

    def test_get_one(self):
        self.test_user = User.objects.create(id=2, username='user', password='123', is_staff=True, is_active=True)
        res = self.client.get(self.user_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_user.username, "user")
        self.assertEqual(self.test_user.is_active, True)

    def test_logout(self):

        data={"refresh_token": self.refresh_token}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_no_refresh_token(self):

        data={"refresh_token": ""}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class FilterAPITestCase(APITestCase):
    def setUp(self) -> None:
        
        self.testuser1 = User.objects.create_superuser(
            username='admintest', password='admin')

        self.client.login(username=self.testuser1.username,
                          password='admin') 
        
        self.user = User.objects.create(username='admin', password='123', is_staff=True, is_active=True)

        self.urls = '{url}?{filter}={value}&{filter1}={value1}&{filter2}={value2}'.format(
            url=reverse('user'),
            filter='is_staff', value='true', filter1='', value1= '', filter2='', value2='')
        
        return super().setUp()
    
    def test_filter_profile(self):
        res = self.client.get(self.urls)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

class UpdatePasswordTest(APITestCase):
    def setUp(self):

        self.test_user = User.objects.create_superuser(id= 1, username='jonh', password='admin')
        self.client.login(username=self.test_user.username, password='admin')
        self.url = reverse('change_password', kwargs={'pk': 1})
        self.admin_url = reverse('admin_change_password', kwargs={'pk': 1})
        self.data = {'old_password': 'admin','password': 'newtestpassword', 'confirm_password': 'newtestpassword'}
        self.admin_data = {'password': 'newtestpassword',}

    def test_update_password(self):
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(username='jonh').check_password('newtestpassword'))

    def test_update_password_with_wrong_old_password(self):
        
        data = {
            "old_password": "wrong_password",
            "password": "new_password",
            "confirm_password": "new_password"
        }
        response = self.client.put(self.url, data)        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('old_password' in response.data.keys())

    def test_update_password_with_wrong_confirm_password(self):
        
        con_data = {
            "old_password": "admin",
            "password": "new_password",
            "confirm_password": "new_password1"
        }
        response = self.client.put(self.url, con_data)        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_update_password(self):
        response = self.client.put(self.admin_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(username='jonh').check_password('newtestpassword'))

