# Generated by Django 3.0.6 on 2020-08-16 21:27

# Imports from Django
import django.db.models.deletion
from django.db import migrations, models

# Local Imports
from core.fields import UpperCaseCharField


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alpha_2_code', UpperCaseCharField(max_length=2, unique=True)),
                ('english_short_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='StateProvince',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', UpperCaseCharField(max_length=2)),
                ('name', models.CharField(max_length=30)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='states_provinces', to='localities.Country')),
            ],
        ),
    ]
