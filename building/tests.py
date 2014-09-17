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

        #haven't added anything yet (via make), so should be None
        #self.assertEqual(result[0], None)
        self.assertEqual(result.building, None)

        result = search_building(a1, make=True)

        #print result

        #trying to add again should just find the same building:
        result2 = search_building(a1, make=True)
        #print result2

        #this works
        #print result.matches == result2.matches
        self.assertEqual(result.matches, result2.matches)
           
        #self.assertEqual(result[0], result2[0])
        #self.assertEqual(result[1], result2[1])
        self.assertEqual(result.building, result2.building)
        self.assertEqual(result.unit, result2.unit)

        a2 = "3210 E JOHN HINKLE PL, Bloomington IN"
        result3 = search_building(a2)
        #print result3

        #not specifying the unit number should still return the building
        #self.assertEqual(result3[0], result2[0])
        self.assertEqual(result3.building, result2.building)

        a4 = "3210 East John HINKLE Place, Bloomington IN"
        result4 = search_building(a4)
        #print result4
        
        #different address formatting should still be the same building:
        #self.assertEqual(result4[0], result2[0])
        self.assertEqual(result4.building, result2.building)
