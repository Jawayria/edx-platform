"""
    API for UserProfile model
"""

from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from common.djangoapps.student.models import (
    UserProfile,
)
from .serializers import UserProfileSerializer


class UsersPagination(PageNumberPagination):
    """
    Defines pagination for UsersAPI
    """
    page_size = 2
    page_size_query_param = 'page_size'


class UserProfileAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    pagination_class = UsersPagination
    queryset=UserProfile.objects.all()

