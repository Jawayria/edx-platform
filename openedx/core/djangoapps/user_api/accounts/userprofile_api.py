"""
    API for UserProfile model
"""

import datetime

from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from common.djangoapps.student.models import (
    UserProfile,
)
from .serializers import UserProfileSerializer


def ratelimit_reached(request, limit, time_unit):
    """
    Checks whether the ratelimit for logged in user has reached
    """

    time_unit_to_secs = {'s':1, 'm':60, 'h':3600, 'd':3600*24}

    if 'rate_limit_value' in request.session:
        request.session['rate_limit_value'] = request.session['rate_limit_value'] + 1
    else:
        request.session['rate_limit_value'] = 1
        request.session['rate_limit_st_time'] = datetime.datetime.now()

    if (datetime.datetime.now() - request.session['rate_limit_st_time']).seconds < time_unit_to_secs[time_unit] and \
        request.session['rate_limit_value'] > limit:
        return True

    return False


class UsersPagination(PageNumberPagination):
    """
    Defines pagination for UsersAPI
    """
    page_size = 2
    page_size_query_param = 'page_size'


class UserProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    pagination_class = UsersPagination
    queryset=''

    def get(self, request, pk=None):

        if ratelimit_reached(request, 10, 'm'):
            return HttpResponse(status=403)

        page = UsersPagination()
        if pk is not None:
            queryset = UserProfile.objects.get(pk=pk)
        else:
            queryset = UserProfile.objects.all()

        serializer = UserProfileSerializer(page.paginate_queryset(queryset, request), many=True)
        return Response(serializer.data)
