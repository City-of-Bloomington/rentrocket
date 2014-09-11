"""
run with:
manage.py test

testing with live / dev data:
scripts/test_searches.py
"""

from django.test import TestCase

from building.models import *

class BuildingTest(TestCase):
    def test_building_creation(self):
        """
        Test that a building gets created
        """
        a1 = "3210 E JOHN HINKLE PL UNIT B, Bloomington IN"
        result = search_building(a1)
        
        self.assertEqual(result[0], None)

        result = search_building(a1, make=True)

        #print result

        result2 = search_building(a1, make=True)
        #print result2
        
        self.assertEqual(result[0], result2[0])
        self.assertEqual(result[1], result2[1])

        a2 = "3210 E JOHN HINKLE PL, Bloomington IN"
        result3 = search_building(a2)
        #print result3
        
        self.assertEqual(result3[0], result2[0])

        a4 = "3210 East John HINKLE Place, Bloomington IN"
        result4 = search_building(a4)
        #print result4
        
        self.assertEqual(result4[0], result2[0])
