# -*- coding: utf-8 -*-


# Imports from Django
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.text import slugify

# Imports from Third Party Modules
from datetime import datetime
from faker import Faker
from mock import MagicMock, patch

# Local Imports
from hikers.tests.factories import HikerFactory

# Local imports
from ..utils import (
    get_file_attr,
    get_max_mb,
    hiker_photos_upload_path,
    profile_pics_upload_path,
    randomize_filename,
    title_hike_or_date_str,
    truncate_slug_text,
    unique_slugify,
    user_directory_path,
    validate_file_has_extension,
    validate_file_upload_size,
)
from .test_models import TestSlugifiedName


class TestSlugifying(models.Model):
    name = models.CharField(max_length=25)
    slug = models.SlugField(blank=True)

    class Meta:
        app_label = 'core'


class CoreUtilsTests(TestCase):

    def test_get_file_attr(self):
        mock_upload_obj = 'CharField'
        with self.assertRaises(ImproperlyConfigured):
            get_file_attr(mock_upload_obj)

        mock_upload_obj = MagicMock()
        mock_upload_obj.file = MagicMock()
        self.assertEquals(get_file_attr(mock_upload_obj), mock_upload_obj.file)

    @patch('core.utils.get_file_attr')
    @patch('core.utils.get_max_m')
    def test_validate_file_upload_size(self, mock_max_mb, mock_file_attr):
        mock_upload_obj = MagicMock()
        mock_file = MagicMock()
        mock_file.size = 6 * 1024 * 1024
        mock_file_attr.return_value = mock_file
        mock_max_mb.return_value = 5
        with self.assertRaises(ValidationError):
            validate_file_upload_size(mock_upload_obj)

    @override_settings(MAX_UPLOAD_SIZE_IN_MB=4)
    def test_get_max_mb_with_settings(self):
        mb_size = None
        self.assertEquals(get_max_mb(mb_size), 4)
        mb_size = 3
        self.assertEquals(get_max_mb(mb_size), 3)
        mb_size = 5
        self.assertEquals(get_max_mb(mb_size), 4)

    def test_get_max_nb_without_settings(self):
        mb_size = None
        with self.assertRaises(ImproperlyConfigured):
            get_max_mb(mb_size)
        mb_size = 7
        self.assertEquals(get_max_mb(mb_size), mb_size)

    def test_randomize_filename(self):
        name = 'myrandomfile'
        ext = 'jpg'
        filename = '{}.{}'.format(name, ext)
        self.assertNotIn(name, randomize_filename(filename))
        self.assertIn(ext, randomize_filename(filename))

    @patch('core.utils.get_file_attr')
    def test_validate_file_ext(self, mock_file_attr):
        name = 'myrandomfile'
        mock_upload_obj = MagicMock()
        mock_file = MagicMock()
        mock_file.name = name
        mock_file_attr.return_value = mock_file
        with self.assertRaises(ValidationError):
            validate_file_has_extension(mock_upload_obj)

    def test_user_directory_path(self):
        instance = TestSlugifiedName()
        with self.assertRaises(ImproperlyConfigured):
            user_directory_path(instance)

        instance = HikerFactory()
        self.assertIn(instance.slug, user_directory_path(instance))

        instance = MagicMock()
        instance.hiker = MagicMock()
        instance.hiker.slug = 'hiker-slug'
        self.assertIn(instance.hiker.slug, user_directory_path(instance))

    @patch('core.utils.user_directory_path')
    @patch('core.utils.randomize_filename')
    def test_profile_pics_upload_path(self, mock_file_name, mock_path):
        mock_file_name.return_value = 'file-name'
        mock_path.return_value = 'user/path'
        self.assertIn('profile_pics',
                      profile_pics_upload_path('instance', 'filename'))

    @patch('core.utils.user_directory_path')
    @patch('core.utils.randomize_filename')
    def test_hiker_photos_upload_path(self, mock_file_name, mock_path):
        mock_file_name.return_value = 'file-name'
        mock_path.return_value = 'user/path'
        self.assertIn('hike_photos',
                      hiker_photos_upload_path('instance', 'filename'))

    def test_unique_slugify(self):
        name = 'Non-unique name'
        slug1 = TestSlugifying.objects.create(name=name)
        slug2 = TestSlugifying.objects.create(name=name)
        slugqs = TestSlugifying.objects.all()
        unique_slug = unique_slugify(slugqs, name)
        self.assertEquals(slugify(name), unique_slug)
        slug1.slug = unique_slug
        slug1.save()
        unique_slug2 = unique_slugify(slugqs, name)
        self.assertIn('1', unique_slug2)
        slug2.slug = slugify('{}-{}'.format(name, 2))
        slug2.save()
        unique_slug3 = unique_slugify(slugqs, name)
        self.assertIn('3', unique_slug3)

    def test_unicode_by_title_hike_or_date(self):

        class TestBadUnicodeMethod(models.Model):
            foo = models.CharField(max_length=25)

            def __str__(self):
                return title_hike_or_date_str(self)

        obj = TestBadUnicodeMethod(foo='bar')
        with self.assertRaises(ImproperlyConfigured):
            obj.__str__()

        date_fmt = '%Y-%m-%d'
        uni_date = datetime.today().strftime(date_fmt)
        obj = MagicMock()
        obj.title = 'Title'
        obj.hike.name = 'Hike Name'
        self.assertIn(obj.title, title_hike_or_date_str(obj))
        self.assertIn(obj.hike.name, title_hike_or_date_str(obj))

        obj.hike = None
        obj.created = datetime.today()
        self.assertIn(obj.title, title_hike_or_date_str(obj))
        self.assertIn(obj.created.strftime(date_fmt),
                      title_hike_or_date_str(obj))

        obj.title = ''
        obj.hike = MagicMock()
        obj.hike.name = 'New Hike Name'
        self.assertIn(obj.hike.name, title_hike_or_date_str(obj))
        self.assertIn(obj.created.strftime(date_fmt),
                      title_hike_or_date_str(obj))

        obj.pk = ''
        obj.title = ''
        obj.hike = None
        obj.created = None
        self.assertIn(uni_date, title_hike_or_date_str(obj))

    def test_truncate_slug_text(self):
        fake = Faker()
        begin = fake.text(max_nb_chars=200)
        mid1 = fake.text(max_nb_chars=25)
        mid2 = fake.text(max_nb_chars=25)
        date_fmt = '%Y-%m-%d'
        end_date = datetime.today().strftime(date_fmt)
        slug_text = fake.text(max_nb_chars=50)
        self.assertEquals(slug_text, truncate_slug_text(slug_text))

        slug_from_begin = truncate_slug_text(begin)
        self.assertNotEquals(begin, slug_from_begin)
        self.assertIn(slug_from_begin, begin)
        self.assertTrue(len(slug_from_begin) <= 50)

        slug_text = '{} - {}'.format(begin, end_date)
        slug_from_begin_date = truncate_slug_text(slug_text)
        self.assertIn(end_date, slug_from_begin_date)
        self.assertTrue(len(slug_from_begin_date) <= 50)

        slug_text = '{} - {} - {} - {}'.format(begin, mid1, mid2, end_date)
        slug_from_many = truncate_slug_text(slug_text)
        self.assertIn(mid1[:9], slug_from_many)
        self.assertNotIn(mid2[:9], slug_from_many)
        self.assertTrue(len(slug_from_many) <= 50)
