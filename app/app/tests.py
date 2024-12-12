from app import cals

from django.test import SimpleTestCase

class CalTest(SimpleTestCase):
    def test_add_nums(self):
        res = cals.add(2,3)
        self.assertEqual(8 , res )