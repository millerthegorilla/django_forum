import typing

from django.conf import settings


def siteName(request) -> typing.Dict[str, str]:
    return {'siteName': settings.SITE_NAME}

def base_html(request):
    return {'BASE_HTML': settings.BASE_HTML}