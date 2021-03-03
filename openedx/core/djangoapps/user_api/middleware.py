"""
Middleware for user api.
Adds user's tags to tracking event context.
"""
import datetime
import pdb
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from eventtracking import tracker
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

from common.djangoapps.track.contexts import COURSE_REGEX

from .models import UserCourseTag


class UserTagsEventContextMiddleware(MiddlewareMixin):
    """Middleware that adds a user's tags to tracking event context."""
    CONTEXT_NAME = 'user_tags_context'

    def process_request(self, request):
        """
        Add a user's tags to the tracking event context.
        """
        match = COURSE_REGEX.match(request.build_absolute_uri())
        course_id = None
        if match:
            course_id = match.group('course_id')
            try:
                course_key = CourseKey.from_string(course_id)
            except InvalidKeyError:
                course_id = None
                course_key = None

        context = {}

        if course_id:
            context['course_id'] = course_id

            if request.user.is_authenticated:
                context['course_user_tags'] = dict(
                    UserCourseTag.objects.filter(
                        user=request.user.pk,
                        course_id=course_key,
                    ).values_list('key', 'value')
                )
            else:
                context['course_user_tags'] = {}

        tracker.get_tracker().enter_context(
            self.CONTEXT_NAME,
            context
        )

    def process_response(self, request, response):  # pylint: disable=unused-argument
        """Exit the context if it exists."""
        try:
            tracker.get_tracker().exit_context(self.CONTEXT_NAME)
        except:  # pylint: disable=bare-except
            pass

        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware that keeps check on the ratelimit
    """

    def process_request(self, request):
        """
        Checks whether the ratelimit for logged in user has reached
        """
        time_unit_to_secs = {'s': 1, 'm': 60, 'h': 3600, 'd': 3600 * 24}
        time_unit = 'm'
        limit = 10

        if 'ratelimit' not in request.session:
            request.session['ratelimit'] = {request.path:{'counter': 1, 'st_time': datetime.datetime.now()}}

        elif request.path not in request.session['ratelimit'] or (datetime.datetime.now() - \
            request.session['ratelimit'][request.path]['st_time']).seconds >= time_unit_to_secs[time_unit]:
            request.session['ratelimit'][request.path] = {'counter': 1, 'st_time': datetime.datetime.now()}

        else:
            request.session['ratelimit'][request.path]['counter'] = \
            request.session['ratelimit'][request.path]['counter'] + 1

        if (datetime.datetime.now() - request.session['ratelimit'][request.path]['st_time']).seconds < \
            time_unit_to_secs[time_unit] and request.session['ratelimit'][request.path]['counter'] > limit:
            return HttpResponse(status=403)

        request.session.modified = True

        return HttpResponse(status=200)
