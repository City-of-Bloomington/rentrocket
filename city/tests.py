"""
This file demonstrates writing tests using the unittest module.

run with:
manage.py test

testing with live / dev data:
scripts/test_searches.py
"""

from django.test import TestCase

from city.models import *

class CityTest(TestCase):
    def test_city_creation(self):
        """
        Test that a city gets created
        """
        #city = make_city("", "IN")
        #(city, error) = find_by_city_state("", "IN", make=True)
        city = find_by_city_state("", "IN")
        
        #city = make_city("Bloomington", "IN")
        #(city, error) = find_by_city_state("Bloomington", "IN", make=True)
        city = find_by_city_state("Bloomington", "IN")
        #print city
        #nothing added yet
        self.assertEqual(city, None)

        #(city, error, results) = search_city("Bloomington, IN", make=True)
        ## print dir(self)
        ## print city
        ## print error
        ## print results
        #self.assertEqual(error, None)

        results = search_city("Bloomington, IN", make=True)
        city = results.city
        self.assertEqual(results.errors, [])
        self.assertNotEqual(city, None)

        results = search_city("Indiana, USA", make=True)
        #print results.errors
        self.assertNotEqual(results.errors, [])

        #'addCleanup', 'addTypeEqualityFunc', 'assertAlmostEqual', 'assertAlmostEquals', 'assertContains', 'assertDictContainsSubset', 'assertDictEqual', 'assertEqual', 'assertEquals', 'assertFalse', 'assertFieldOutput', 'assertFormError', 'assertFormsetError', 'assertGreater', 'assertGreaterEqual', 'assertHTMLEqual', 'assertHTMLNotEqual', 'assertIn', 'assertInHTML', 'assertIs', 'assertIsInstance', 'assertIsNone', 'assertIsNot', 'assertIsNotNone', 'assertItemsEqual', 'assertJSONEqual', 'assertLess', 'assertLessEqual', 'assertListEqual', 'assertMultiLineEqual', 'assertNotAlmostEqual', 'assertNotAlmostEquals', 'assertNotContains', 'assertNotEqual', 'assertNotEquals', 'assertNotIn', 'assertNotIsInstance', 'assertNotRegexpMatches', 'assertNumQueries', 'assertQuerysetEqual', 'assertRaises', 'assertRaisesMessage', 'assertRaisesRegexp', 'assertRedirects', 'assertRegexpMatches', 'assertSequenceEqual', 'assertSetEqual', 'assertTemplateNotUsed', 'assertTemplateUsed', 'assertTrue', 'assertTupleEqual', 'assertXMLEqual', 'assertXMLNotEqual', 'assert_', 'atomics', 'available_apps', 'client', 'client_class', 'countTestCases', 'debug', 'defaultTestResult', 'doCleanups', 'fail', 'failIf', 'failIfAlmostEqual', 'failIfEqual', 'failUnless', 'failUnlessAlmostEqual', 'failUnlessEqual', 'failUnlessRaises', 'failureException', 'id', 'longMessage', 'maxDiff', 'reset_sequences', 'restore_warnings_state', 'run', 'save_warnings_state', 'setUp', 'setUpClass', 'settings', 'shortDescription', 'skipTest', 'tearDown', 'tearDownClass', 'test_city_creation']

        city2 = find_by_city_state("Bloomington", "IN")
        #print city2
        #nothing added yet
        self.assertEqual(city, city2)
