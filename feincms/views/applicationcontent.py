# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------

import re
try:
    from email.utils import parsedate
except ImportError: # py 2.4 compat
    from email.Utils import parsedate

from django.http import Http404

from feincms import settings
from feincms.content.application.models import ApplicationContent
from feincms.module.page.models import Page
from feincms.views.base import Handler


def applicationcontent_request_processor(page, request):
    request._feincms_extra_context['in_appcontent_subpage'] = False

    if request.path != page.get_absolute_url():
        # The best_match logic kicked in. See if we have at least one
        # application content for this page, and raise a 404 otherwise.
        if not page.content.all_of_type(ApplicationContent):
            if not settings.FEINCMS_ALLOW_EXTRA_PATH:
                raise Http404
        else:
            request._feincms_extra_context['in_appcontent_subpage'] = True

        request._feincms_extra_context['extra_path'] = re.sub(
            '^' + re.escape(page.get_absolute_url()[:-1]), '', request.path)

Page.register_request_processors(applicationcontent_request_processor)


class ApplicationContentHandler(Handler):
    def __call__(self, request, path=None):
        return self.build_response(request,
            Page.objects.best_match_for_path(path or request.path, raise404=True))

handler = ApplicationContentHandler()
