from django.test import TestCase, Client


class IndexPage(TestCase):
    def test_index_exists(self):
        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_uses_proper_template(self):
        c = Client()
        response = c.get('/')
        self.assertTemplateUsed(response, 'mainshop/index.html')


class ActivationPage(TestCase):
    def test_activation_page_exists(self):
        c = Client()
        response = c.get('/activate/abcdefgh/')
        self.assertEqual(response.status_code, 200)

    def test_activation_uses_proper_template(self):
        c = Client()
        response = c.get('/activate/abcdefgh/')
        self.assertTemplateUsed(response, 'mainshop/activated.html')
