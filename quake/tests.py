from django.test import TestCase
from .models import Earthquake
from datetime import date

class EarthquakeModelTest(TestCase):
    def test_create_earthquake(self):
        eq = Earthquake.objects.create(date=date(2023, 5, 1), magnitude=5.0, location='Tokyo')
        self.assertEqual(eq.magnitude, 5.0)
        self.assertEqual(eq.location, 'Tokyo')
