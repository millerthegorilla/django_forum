# Generated by Django 3.1.5 on 2021-03-27 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_profile', '0002_auto_20210324_1010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='display_name',
            field=models.CharField(blank=True, default='9991572a-d5fe-4c08-9fe8-aa9441ae5014', max_length=37, unique=True),
        ),
    ]
