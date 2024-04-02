from django.contrib.auth.models import User
from django.test import TestCase

from apps.models import Class


class BaseTestCase(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
        )
        self.user.is_staff = True
        self.user.save()

    def login(self):
        self.client.login(username=self.username, password=self.password)

    def logout(self):
        self.client.logout()


class TestLogin(BaseTestCase):
    def test_login_right(self):
        response = self.client.post('/login/', {'username': self.username, 'password': self.password})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_login_wrong(self):
        response = self.client.post('/login/', {'username': self.username, 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')


class TestClassList(BaseTestCase):
    def test_class_list(self):
        class_name = ['Class A', 'Class B', 'Class C']
        for name in class_name:
            Class.objects.create(name=name)
        response = self.client.get('/class/')
        self.assertEqual(response.status_code, 200)
        for name in class_name:
            self.assertContains(response, name)
        self.client.logout()
        self.assertEqual(response.status_code, 200)
        for name in class_name:
            self.assertContains(response, name)


class TestClassDetail(BaseTestCase):
    def test_class_detail(self):
        class_name = 'Class A'
        class_instance_name = ['Instance A', 'Instance B', 'Instance C']
        class_instance = Class.objects.create(name=class_name)
        for name in class_instance_name:
            class_instance.instance_set.create(name=name)
        response = self.client.get(f'/class/{class_instance.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, class_name)
        for name in class_instance_name:
            self.assertContains(response, name)
        self.client.logout()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, class_name)
        for name in class_instance_name:
            self.assertContains(response, name)


class TestInstanceList(BaseTestCase):
    def test_instance_list(self):
        class_name = 'Class A'
        class_instance_name = ['Instance A', 'Instance B', 'Instance C']
        class_instance = Class.objects.create(name=class_name)
        for name in class_instance_name:
            class_instance.instance_set.create(name=name)
        response = self.client.get('/instance/')
        self.assertEqual(response.status_code, 200)
        for name in class_instance_name:
            self.assertContains(response, name)
        self.client.logout()
        self.assertEqual(response.status_code, 200)
        for name in class_instance_name:
            self.assertContains(response, name)


class TestInstanceDetail(BaseTestCase):
    def test_instance_detail(self):
        class_name = 'Class A'
        class_instance_name = 'Instance A'
        class_instance = Class.objects.create(name=class_name)
        instance = class_instance.instance_set.create(name=class_instance_name)
        response = self.client.get(f'/instance/{instance.id}/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/instance/{class_instance.id}/wiki')


class TestInstanceWiki(BaseTestCase):
    def setUp(self):
        super().setUp()
        class_name = 'Class A'
        class_instance_name = 'Instance A'
        class_instance = Class.objects.create(name=class_name)
        self.instance = class_instance.instance_set.create(name=class_instance_name)
        self.login()

    def test_instance_wiki_default(self):
        class_name = 'Class A'
        class_instance_name = 'Instance A'
        class_instance = Class.objects.create(name=class_name)
        instance = class_instance.instance_set.create(name=class_instance_name)
        self.login()
        response = self.client.get(f'/instance/{instance.id}/wiki')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wiki')
        self.assertContains(response, 'Some properties required for wiki are missing')

    def test_instance_wiki_raw(self):
        response = self.client.get(f'/instance/{self.instance.id}/raw')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Raw')
        # allow to edit
        self.assertContains(response, 'Edit')
        self.logout()
        response = self.client.get(f'/instance/{self.instance.id}/raw')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Raw')
        self.assertNotContains(response, 'Edit')


class TestInstanceCreateWikiProperty(BaseTestCase):
    def setUp(self):
        super().setUp()
        class_name = 'Class A'
        class_instance_name = 'Instance A'
        class_instance = Class.objects.create(name=class_name)
        self.instance = class_instance.instance_set.create(name=class_instance_name)
        self.login()

    def test_instance_create_wiki_property(self):
        response = self.client.get(f'/instance/{self.instance.id}/create_wiki_property/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/instance/{self.instance.id}/property/')
        response = self.client.get(f'/instance/{self.instance.id}/property/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'wikiContent')
        self.assertContains(response, 'wikiImage')
        self.assertContains(response, 'wikiTitle')

    def test_instance_create_wiki_property_not_login(self):
        self.logout()
        response = self.client.get(f'/instance/{self.instance.id}/create_wiki_property/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/login/?next=/instance/1/create_wiki_property/')
