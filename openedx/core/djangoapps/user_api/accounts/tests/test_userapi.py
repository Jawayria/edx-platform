# -*- coding: utf-8 -*-
"""
Unit tests for behavior that is specific to the user api methods
"""
import pdb
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from common.djangoapps.student.tests.factories import UserFactory

from openedx.core.djangoapps.user_api.accounts.userprofile_api import UserProfileAPIView

PASSWORD = 'dummy'

class TestUser(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.view = UserProfileAPIView.as_view()
        self.uri = reverse('users_list')
        self.user = UserFactory.create(password=PASSWORD)
        self.client.login(username=self.user.username, password=PASSWORD)

    def test_list(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))

    def test_user_get_ratelimit(self):

        for _ in range(10):
            response = self.client.get(self.uri)
            self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))

        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 403,
                         'Expected Response Code 403, received {0} instead.'
                         .format(response.status_code))
