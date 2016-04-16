# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-16 15:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hikers', '0001_initial'),
        ('hikes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HikePhotos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('photo', models.ImageField(blank=True,
                                            upload_to=b'hike_photos')),
                ('hike', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='hike_photos', to='hikes.Hike')),
                ('hiker', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='hike_photos_by_hiker', to='hikers.Hiker')),
            ],
            options={
                'ordering': ['-modified'],
            },
        ),
        migrations.CreateModel(
            name='HikeReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('review', models.TextField()),
                ('hike', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reviews_by_hike', to='hikes.Hike')),
                ('hiker', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='reviews_by_hiker', to='hikers.Hiker')),
            ],
            options={
                'ordering': ['-modified'],
            },
        ),
    ]
