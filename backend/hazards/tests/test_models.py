# -*- coding: utf-8 -*-

# Imports from Django
from django.test import TestCase
from django.utils import timezone

# Imports from Third Party Modules
import mock

# Local Imports
from hikers.tests.factories import HikerFactory

# Local imports
from ..models import Hazard
from .factories import HazardFactory


class HazardsModelTests(TestCase):

    def test_hazard_unicode(self):
        date_fmt = '%Y-%m-%d'
        hazard = HazardFactory()
        self.assertIsInstance(hazard, Hazard)
        self.assertIn(hazard.created.strftime(date_fmt),
                      hazard.__str__())
        self.assertIn(hazard.hazard_type,
                      hazard.__str__())

    @mock.patch('hazards.models.deleted_hiker_fallback')
    def test_hazard_save(self, mock_deleted_hiker_fallback):
        reported = HikerFactory()
        empty = HikerFactory()
        mock_deleted_hiker_fallback.return_value = empty
        save_hazard = HazardFactory(reported_by=reported)
        save_hazard.save()
        self.assertFalse(mock_deleted_hiker_fallback.called)
        self.assertEquals(mock_deleted_hiker_fallback.call_count, 0)

        save_hazard.reported_by = None
        save_hazard.save()
        self.assertTrue(mock_deleted_hiker_fallback.called)
        self.assertEquals(mock_deleted_hiker_fallback.call_count, 1)
        self.assertIsNone(save_hazard.resolution_reported_by)

        save_hazard.resolution_reported_by = reported
        save_hazard.save()
        self.assertEquals(mock_deleted_hiker_fallback.call_count, 1)

        save_hazard.date_resolved = timezone.now()
        save_hazard.save()
        self.assertEquals(mock_deleted_hiker_fallback.call_count, 1)

        save_hazard.resolution_reported_by = None
        save_hazard.save()
        self.assertEquals(mock_deleted_hiker_fallback.call_count, 2)
