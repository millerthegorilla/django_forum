# Generated by Django 4.1.5 on 2023-01-18 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_forum', '0002_alter_comment_author_alter_post_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forumprofile',
            name='postcode',
            field=models.CharField(blank=True, default='', max_length=10, verbose_name='postcode'),
        ),
    ]
