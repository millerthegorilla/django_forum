from django.contrib import admin
from django.urls import path, include
from django_forum import urls as forum_urls
from django.conf import settings
from django.conf.urls.static import static

from django_email_verification import urls as email_urls

from django_users import urls as users_urls

urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path("admin/", admin.site.urls),
    path("", include(forum_urls)),
    path("", include(users_urls)),
    path("tinymce/", include("tinymce.urls")),
    path("email/", include(email_urls)),
]

try:
    settings.DEBUG
except NameError:
    pass
else:
    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
