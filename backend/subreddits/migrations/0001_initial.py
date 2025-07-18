# Generated by Django 5.2.4 on 2025-07-13 10:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Subreddit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=21, unique=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9_]+$', 'Subreddit names can only contain letters, numbers, and underscores.')])),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('icon', models.ImageField(blank=True, null=True, upload_to='subreddit_icons/')),
                ('banner', models.ImageField(blank=True, null=True, upload_to='subreddit_banners/')),
            ],
        ),
    ]
