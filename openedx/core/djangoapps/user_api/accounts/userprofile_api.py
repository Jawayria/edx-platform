"""
    API for UserProfile model
"""

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination


from common.djangoapps.student.models import (
    UserProfile,
)
from django.utils.decorators import method_decorator
from .serializers import UserProfileSerializer


class UsersPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'


class UserProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    pagination_class = UsersPagination
    queryset=''

    @method_decorator(ratelimit(key='user', rate='1/m', method='GET'))
    def get(self, request, pk=None):
        page = UsersPagination()
        if pk is not None:
            queryset = UserProfile.objects.get(pk=pk)
        else:
            queryset = UserProfile.objects.all()

        serializer = UserProfileSerializer(page.paginate_queryset(queryset, request), many=True)
        return Response(serializer.data)
