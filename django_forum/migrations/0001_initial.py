# Generated by Django 4.1.3 on 2022-11-22 00:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_forum.models
import safe_imagefield.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Avatar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_file', safe_imagefield.models.SafeImageField(allowed_extensions=None, check_content_type=False, max_size_limit=False, media_integrity=False, scan_viruses=False, upload_to=django_forum.models.user_directory_path_avatar)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default='True')),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('text', models.TextField(max_length=3000)),
                ('moderation_date', models.DateField(blank=True, default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(max_length=80, unique=True)),
                ('title', models.CharField(default='', max_length=100)),
                ('pinned', models.SmallIntegerField(default=0)),
                ('commenting_locked', models.BooleanField(default=False)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_related', to=settings.AUTH_USER_MODEL)),
                ('subscribed_users', models.ManyToManyField(blank=True, related_name='subscribed_posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'permissions': [('approve_post', 'Approve Post')],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ForumProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_line_1', models.CharField(blank=True, default='', max_length=30, verbose_name='address line 1')),
                ('address_line_2', models.CharField(blank=True, default='', max_length=30, verbose_name='address line 2')),
                ('city', models.CharField(blank=True, default='', max_length=30, verbose_name='city')),
                ('country', models.CharField(blank=True, default='', max_length=30, verbose_name='country')),
                ('postcode', models.CharField(blank=True, default='', max_length=6, verbose_name='postcode')),
                ('rules_agreed', models.BooleanField(default='False')),
                ('display_name', models.CharField(blank=True, default=django_forum.models.default_display_name, max_length=37, unique=True)),
                ('avatar', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to='django_forum.avatar')),
                ('profile_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default='True')),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('text', models.TextField(max_length=3000)),
                ('moderation_date', models.DateField(blank=True, default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(max_length=80, unique=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_related', to=settings.AUTH_USER_MODEL)),
                ('post_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='django_forum.post')),
            ],
            options={
                'ordering': ['created_at'],
                'permissions': [('approve_comment', 'Approve Comment')],
                'abstract': False,
            },
        ),
    ]
