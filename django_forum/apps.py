import os
import importlib
from collections import OrderedDict

from django.apps import apps, AppConfig
from django.conf import settings
from django.core.management import call_command

from pipeline import templates as pipeline_templates
from tinymce import templates as tiny_templates

from django_profile import templates as profile_templates
from django_messages import templates as messages_templates

# my_apps = [
#     {"name": "django_profile", "templates": profile_templates},
#     {
#         "name": "django_messages",
#         "templates": messages_templates,
#     },
#     {"name": "pipeline", "templates": pipeline_templates},
#     {"name": "sorl.thumbnail", "templates": ""},
#     {"name": "tinymce", "templates": tiny_templates},
# ]


# class DjangoForumConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "django_forum"

#     def ready(self) -> None:
#         global my_apps
#         try:
#             if not settings.TOPLEVELCONFIG:
#                 settings.TOPLEVELCONFIG = self.__class__
#                 self.populate_my_apps()
#                 self.install_apps()
#         except AttributeError:
#             settings.TOPLEVELCONFIG = self.__class__
#             self.populate_my_apps()
#             self.install_apps()

#     def populate_my_apps(self):
#         global my_apps
#         for app in my_apps:
#             try:
#                 theapp = importlib.import_module(app["name"] + ".apps")
#                 my_apps += [app for app in theapp.my_apps if app not in my_apps]
#                 app["setup"] = theapp.setup_apps
#             except (ModuleNotFoundError, AttributeError):
#                 pass

#     def install_apps(self):
#         apps.app_configs = OrderedDict()
#         apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
#         apps.clear_cache()
#         for app in my_apps:
#             if app["name"] not in settings.INSTALLED_APPS:
#                 settings.INSTALLED_APPS += (app["name"],)
#                 if app["templates"] != "":
#                     settings.TEMPLATES[0]["DIRS"].append(
#                         os.path.abspath(app["templates"].__path__._path[0])
#                     )
#                 static = os.path.abspath(
#                     importlib.import_module(app["name"]).__path__[0] + "/static/"
#                 )
#                 if os.path.isdir(static):
#                     settings.STATICFILES_DIRS += [static]
#                 # if "setup" in app:
#                 #     app["setup"]()
#         apps.populate(settings.INSTALLED_APPS)
#         for app in my_apps:
#             if (
#                 call_command("findstatic", app["name"], verbosity=0).count(app["name"])
#                 > 3
#             ):
#                 settings.STATICFILES_DIRS = [
#                     x for x in settings.STATICFILES_DIRS if app["name"] not in x
#                 ]
#         try:
#             self.setup_apps()
#         except AttributeError:
#             pass

#     def setup_apps(self):
#         settings.STATICFILES_STORAGE = "pipeline.storage.PipelineManifestStorage"
#         settings.STATICFILES_FINDERS.append("pipeline.finders.PipelineFinder")

#         default_stylesheet_extra_content = {
#             "media": "all",
#             "charset": "UTF-8",
#             "title": None,
#         }

#         default_js_extra_content = {
#             "async": True,
#             "defer": False,
#         }
#         settings.PIPELINE = {
#             "PIPELINE_ENABLED": True,
#             "JS_COMPRESSOR": "pipeline.compressors.jsmin.JSMinCompressor",
#             "CSS_COMPRESSOR": "pipeline.compressors.csshtmljsminify.CssHtmlJsMinifyCompressor",  # noqa: E501
#             "STYLESHEETS": {
#                 "main_styles": {
#                     "source_filenames": (
#                         "django_artisan/css/styles.css",
#                         "django_forum/css/styles.css",
#                     ),
#                     "output_filename": "css/styles_min.css",
#                     "extra_context": default_stylesheet_extra_content,
#                 },
#                 "registration_styles": {
#                     "source_filenames": ("django_users/css/balloons.css",),
#                     "output_filename": "css/blns_min.css",
#                     "extra_context": default_stylesheet_extra_content,
#                 },
#                 "carousel_styles": {
#                     "source_filenames": ("django_bs_carousel/css/styles.css",),
#                     "output_filename": "css/crsl_min.css",
#                     "extra_context": default_stylesheet_extra_content,
#                 },
#             },
#             "JAVASCRIPT": {
#                 "django_bs_carousel": {
#                     "source_filenames": ("django_bs_carousel/js/carousel.js",),
#                     "output_filename": "django_bs_carousel/js/c_min.js",
#                     "extra_context": default_js_extra_content,
#                 },
#                 "django_bs_image_loader": {
#                     "source_filenames": ("django_bs_carousel/js/imageLoader.js",),
#                     "output_filename": "django_bs_carousel/js/il_min.js",
#                     "extra_context": default_js_extra_content,
#                 },
#                 "django_forum": {
#                     "source_filenames": ("django_forum/js/*.js",),
#                     "output_filename": "js/df_min.js",
#                     "extra_context": default_js_extra_content,
#                 },
#                 "django_artisan": {
#                     "source_filenames": ("django_artisan/js/profileUpdate.js",),
#                     "output_filename": "js/da_min.js",
#                     "extra_context": default_js_extra_content,
#                 },
#             },
#         }

#         from tinymce import urls as tinymce_urls  # include the urls
#         from django import urls

#         root_url = importlib.import_module(settings.ROOT_URLCONF)
#         if (
#             urls.path("tinymce/", urls.include(tinymce_urls))
#             not in root_url.urlpatterns
#         ):
#             root_url.urlpatterns.append(
#                 urls.path("tinymce/", urls.include(tinymce_urls))
#             )
