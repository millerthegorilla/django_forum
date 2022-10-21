import os

from setuptools import find_packages, setup

# Optional project description in README.md:

current_directory = os.path.dirname(os.path.abspath(__file__))

try:

    with open(os.path.join(current_directory, "README.md"), encoding="utf-8") as f:

        long_description = f.read()

except Exception:

    long_description = "django_forum extends django_messages, includes django_users \
                         and django_profile and provides a basic forum."

setup(
    # Project name:
    name="django-forum",
    # Packages to include in the distribution:
    packages=find_packages(","),
    # Project version number:
    version="0.0.1",
    # List a license for the project, eg. MIT License
    license="MIT",
    # Short description of your library:
    description="A simple django app to provide a basic forum",
    # Long description of your library:
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Your name:
    author="James Miller",
    # Your email address:
    author_email="jamesstewartmiller@gmail.com",
    # Link to your github repository or website:
    url="https://github.com/millerthegorilla/django_forum",
    # Download Link from where the project can be downloaded from:
    download_url="https://github.com/millerthegorilla/django_forum",
    # List of keywords:
    keywords=["django", "django_forum", "forum app"],
    # List project dependencies:
    install_requires=[
        "django>=4.0.1",
        "django_messages @ git+ssh://git@github.com/millerthegorilla/django_messages#egg=django_messages",  # noqa: E501
        "django_profile @ git+ssh://git@github.com/millerthegorilla/django_profile#egg=django_profile",  # noqa: E501
        "safe_imagefield @ git+ssh://git@github.com/millerthegorilla/safe_imagefield#egg==safe_imagefield",  # noqa: E501
        "random_username>=1.0.2",
        "sorl-thumbnail>=12.9.0",
        "elasticsearch_dsl>=7.4.0",
        "django_elasticsearch_dsl>=7.2.2",
        "django_tinymce>=3.5.0",
        "css_html_js_minify>=2.5.5",
        "jsmin>=3.0.1",
    ],
    # https://pypi.org/classifiers/
    classifiers=[
        "DevelopmentStatus::2-Pre-Alpha",
        "Framework::Django CMS",
        "Framework::Django::4.0",
    ],
)
