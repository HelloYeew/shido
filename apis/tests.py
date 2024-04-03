from django.test import TestCase

from apps.models import Class, Instance
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
        response = self.client.get('/api/class?class=300')
        self.assertEqual(response.status_code, 404)


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


class TestGetInstance(TestCase):
    def setUp(self):
        class_name = ['Class A', 'Class B', 'Class C']
        for name in class_name:
            Class.objects.create(name=name)
        for i in range(3):
            Instance.objects.create(class_instance_id=i + 1, name=f'Instance {i + 1}')

    def test_get_instance_from_class(self):
        response = self.client.get('/api/instance?class=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['instance']), 1)

    def test_get_instance_from_class_fail(self):
        response = self.client.get('/api/instance?class=300')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/api/instance')
        self.assertEqual(response.status_code, 400)

    def test_get_specific_instance(self):
        response = self.client.get('/api/instance/1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json())

    def test_get_specific_instance_fail(self):
        response = self.client.get('/api/instance/300')
        self.assertEqual(response.status_code, 404)


class TestGetRandomInstance(TestCase):
    def setUp(self):
        class_name = ['Class A', 'Class B', 'Class C']
        for name in class_name:
            Class.objects.create(name=name)
        for class_objec in Class.objects.all():
            for i in range(5):
                Instance.objects.create(class_instance=class_objec, name=f'Instance {i + 1}')

    def test_get_random_instance_from_class(self):
        response = self.client.get('/api/instance/random_from_class?class=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['instance']), 1)
        response = self.client.get('/api/instance/random_from_class?class=1&number=3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['instance']), 3)

    def test_get_random_instance_from_class_fail(self):
        response = self.client.get('/api/instance/random_from_class?class=300')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/api/instance/random_from_class')
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/api/instance/random_from_class?class=1&number=10')
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/api/instance/random_from_class?class=1&number=-1')
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/api/instance/random_from_class?class=1&number=0')
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/api/instance/random_from_class?class=1&number=number')
        self.assertEqual(response.status_code, 400)
