from django.test import TestCase

from apps.models import Class
from apps.tests import TestAddWikiProperty


class TestGetClass(TestCase):
    def test_get_class(self):
        class_name = ['Class A', 'Class B', 'Class C']
        for name in class_name:
            Class.objects.create(name=name)
        response = self.client.get('/api/class?class=1')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/class?class=')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['class']), 3)


class TestGetPropertyType(TestAddWikiProperty):
    # Inherit from TestAddWikiProperty to get the wiki creation value too
    def test_get_property_type(self):
        self.client.get(f'/instance/{self.instance.id}/create_wiki_property/')
        response = self.client.get('/api/property_type?class=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['property_type']), 3)

    def test_get_property_type_fail(self):
        response = self.client.get('/api/property_type?class=300')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/api/property_type')
        self.assertEqual(response.status_code, 400)
