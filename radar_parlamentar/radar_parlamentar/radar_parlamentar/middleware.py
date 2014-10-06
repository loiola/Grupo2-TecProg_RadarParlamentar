class ConsoleExceptionMiddleware:

    """Custom middleware to print stack traces on Django console"""

    def process_exception(self, request, exception):
        import traceback
        import sys

        # Receives sys.exc_info () method
        exc_info = sys.exc_info()

        # Receives the format exception coming from traceback
        exception = traceback.format_exception(*(exc_info or sys.exc_info()))

        print "######################## Exception ###########################"
        print '\n'.join(exception)
        print "##############################################################"


from django.middleware.cache import UpdateCacheMiddleware
import re


class SmartUpdateCacheMiddleware(UpdateCacheMiddleware):

    # Receives the method compile() coming from re
    STRIP_RE = re.compile(r'\b(_[^=]+=.+?(?:; |$))')

    def process_request(self, request):

        # Store cookies
        cookie = self.STRIP_RE.sub('', request.META.get('HTTP_COOKIE', ''))
        
        request.META['HTTP_COOKIE'] = cookie
