# Generated by Django 3.1.6 on 2021-03-14 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_artisan', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='artisanforumprofile',
            name='display_personal_page',
            field=models.BooleanField(default=False, verbose_name='Display personal page'),
        ),
    ]
