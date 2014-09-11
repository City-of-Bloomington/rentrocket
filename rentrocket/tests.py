"""
run with:
manage.py test

testing with live / dev data:
scripts/test_searches.py
"""

from django.test import TestCase

from rentrocket.helpers import address_search

class HelpersTest(TestCase):
    def test_address_search(self):
        """
        check that lookups happen appropriately
        (this shouldn't require database connections)
        """
        a1 = "3210 E JOHN HINKLE PL UNIT B, Bloomington IN"
        (options, error, unit) = address_search(a1)

        self.assertEqual(unit, "Unit B")

        self.assertEqual(len(options), 1)

        #print options
        #print error
        
        ## result = search_building(a1)
        
        ## self.assertEqual(result[0], None)

        ## result = search_building(a1, make=True)

        ## #print result

        ## result2 = search_building(a1, make=True)
        ## #print result2
        
        ## self.assertEqual(result[0], result2[0])
        ## self.assertEqual(result[1], result2[1])

        ## a2 = "3210 E JOHN HINKLE PL, Bloomington IN"
        ## result3 = search_building(a2)
        ## #print result3
        
        ## self.assertEqual(result3[0], result2[0])

        ## a4 = "3210 East John HINKLE Place, Bloomington IN"
        ## result4 = search_building(a4)
        ## #print result4
        
        ## self.assertEqual(result4[0], result2[0])
