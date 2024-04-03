from django.contrib.auth.models import User
from django.test import TestCase

from apps.models import Class, PropertyType


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

    def set_as_superuser(self):
        self.user.is_superuser = True
        self.user.save()


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


class TestClassCreate(BaseTestCase):
    def test_class_create(self):
        self.login()
        response = self.client.get('/class/create/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create a new class')
        response = self.client.post('/class/create/', {'name': 'Class A'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/class/')

    def test_class_create_not_login(self):
        self.logout()
        response = self.client.get('/class/create/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/?next=/class/create/')
        response = self.client.post('/class/create/', {'name': 'Class A'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/?next=/class/create/')

    def test_class_create_not_staff(self):
        self.user.is_staff = False
        self.user.save()
        self.login()
        response = self.client.get('/class/create/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/?next=/class/create/')
        response = self.client.post('/class/create/', {'name': 'Class A'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/?next=/class/create/')

    def test_class_create_same_name(self):
        self.login()
        response = self.client.post('/class/create/', {'name': 'Class A'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/class/')
        response = self.client.post('/class/create/', {'name': 'Class A'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')


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


class TestAddWikiProperty(BaseTestCase):
    def setUp(self):
        super().setUp()
        class_name = 'Class A'
        class_instance_name = 'Instance A'
        class_instance = Class.objects.create(name=class_name)
        self.instance = class_instance.instance_set.create(name=class_instance_name)
        self.login()

    def test_add_wiki_content(self):
        self.client.get(f'/instance/{self.instance.id}/create_wiki_property/')
        wiki_content_property_id = PropertyType.objects.get(name='wikiContent', class_instance_id=self.instance.class_instance.id).id
        response = self.client.get(f'/instance/{self.instance.id}/property/{wiki_content_property_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'wikiContent')
        self.assertContains(response, 'No limitation set')
        self.assertContains(response, 'name="value"')
        # wikiContent is markdown and use textarea for input
        self.assertContains(response, 'class="form-control textarea"')
        response = self.client.post(f'/instance/{self.instance.id}/property/{wiki_content_property_id}/', {'value': 'contentTESTTEST'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/instance/{self.instance.id}/raw')
        response = self.client.get(f'/instance/{self.instance.id}/raw')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'ID : {wiki_content_property_id}')
        self.assertContains(response, 'contentTESTTEST')

    def test_add_wiki_image(self):
        self.client.get(f'/instance/{self.instance.id}/create_wiki_property/')
        wiki_image_property_id = PropertyType.objects.get(name='wikiImage', class_instance_id=self.instance.class_instance.id).id
        response = self.client.get(f'/instance/{self.instance.id}/property/{wiki_image_property_id}/')
        self.assertEqual(response.status_code, 200)
        # Just test that the form contains the image input
        self.assertContains(response, 'wikiImage')
        self.assertContains(response, 'No limitation set')
        self.assertContains(response, 'type="file"')
        self.assertContains(response, 'accept="image/*"')

    def test_add_wiki_title(self):
        self.client.get(f'/instance/{self.instance.id}/create_wiki_property/')
        wiki_title_property_id = PropertyType.objects.get(name='wikiTitle',
                                                          class_instance_id=self.instance.class_instance.id).id
        response = self.client.get(f'/instance/{self.instance.id}/property/{wiki_title_property_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'wikiTitle')
        # Check limitation
        self.assertContains(response, 'max_length : 255')
        self.assertContains(response, 'min_length : 1')
        self.assertContains(response, 'class="form-control textinput"')
        response = self.client.post(f'/instance/{self.instance.id}/property/{wiki_title_property_id}/', {'value': 'titleTEST'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/instance/{self.instance.id}/raw')
        response = self.client.get(f'/instance/{self.instance.id}/raw')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'titleTEST')

    def test_add_wiki_title_failed(self):
        self.client.get(f'/instance/{self.instance.id}/create_wiki_property/')
        wiki_title_property_id = PropertyType.objects.get(name='wikiTitle',
                                                          class_instance_id=self.instance.class_instance.id).id
        property = PropertyType.objects.get(id=wiki_title_property_id)
        property.limitation = {'max_length': 255, 'min_length': 5}
        property.save()
        response = self.client.get(f'/instance/{self.instance.id}/property/{wiki_title_property_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'wikiTitle')
        response = self.client.post(f'/instance/{self.instance.id}/property/{wiki_title_property_id}/', {'value': 'x'*10000})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The value must not be longer than')
        response = self.client.post(f'/instance/{self.instance.id}/property/{wiki_title_property_id}/', {'value': 'x'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The value must not be shorter than')

    def test_add_wiki_property_not_login(self):
        self.logout()
        response = self.client.get(f'/instance/{self.instance.id}/create_wiki_property/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/login/?next=/instance/1/create_wiki_property/')
        response = self.client.get(f'/instance/{self.instance.id}/property/1/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/login/?next=/instance/1/property/1/')

    def test_wiki_page_after_adding_properties(self):
        self.test_add_wiki_title()
        self.test_add_wiki_content()
        self.test_add_wiki_image()
        response = self.client.get(f'/instance/{self.instance.id}/wiki')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'titleTEST')
        self.assertContains(response, 'contentTESTTEST')

    def test_homepage(self):
        self.test_add_wiki_title()
        self.test_add_wiki_content()
        self.test_add_wiki_image()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Home')
        self.assertContains(response, 'Total Class')
        self.assertContains(response, '1')
        self.assertContains(response, 'Total Instance')
        self.assertContains(response, '1')


class TestPropertyType(BaseTestCase):
    def setUp(self):
        super().setUp()
        class_name = 'Class A'
        class_instance_name = 'Instance A'
        class_instance = Class.objects.create(name=class_name)
        self.instance = class_instance.instance_set.create(name=class_instance_name)
        self.login()

    def test_property_type(self):
        # Create wiki properties for testing
        self.client.get(f'/instance/{self.instance.id}/create_wiki_property/')
        response = self.client.get(f'/instance/{self.instance.id}/property/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Property Type')
        self.assertContains(response, 'wikiContent')
        self.assertContains(response, 'Raw type : Markdown')
        self.assertContains(response, 'wikiImage')
        self.assertContains(response, 'Raw type : Image')
        self.assertContains(response, 'wikiTitle')
        self.assertContains(response, 'Raw type : String')