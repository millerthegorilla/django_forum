# Generated by Django 3.2 on 2021-05-21 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_artisan', '0003_auto_20210323_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artisanforumprofile',
            name='bio',
            field=models.TextField(blank=True, default='', max_length=500, verbose_name='biographical information, max 500 chars'),
        ),
    ]
