from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth.models import User
from mainshop.models import Customer



class RegistrationTests(TestCase):
    def setUp(self) -> None:
        self.good_request = {
            'firstname': 'Billy',
            'lastname': 'Bob',
            'email': 'billy.bob@gmail.com',
            'password': '*****',
            'address': 'Trg Dositeja Obradovića 6',
            'city': 'Novi Sad',
            'zipcode': '21000',
        }
        self.good_request_2 = {
            'firstname': 'Fannie',
            'lastname': 'Mae',
            'email': 'fannie.mae@gmail.com',
            'password': '*****',
            'address': 'Trg Dositeja Obradovića 6',
            'city': 'Novi Sad',
            'zipcode': '21000',
        }
        self.bad_request_missing_field = {
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john.doe@gmail.com',
            'address': 'Trg Dositeja Obradovića 6',
            'city': 'Novi Sad',
            'zipcode': '21000',
        }
        self.bad_request_bad_email = {
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john.doe/gmail.com',
            'password': '*****',
            'address': 'Trg Dositeja Obradovića 6',
            'city': 'Novi Sad',
            'zipcode': '21000',
        }
        self.bad_request_empty_field = {
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john.doe@gmail.com',
            'password': '*****',
            'address': '',
            'city': 'Novi Sad',
            'zipcode': '21000',
        }

    @classmethod
    def setUpTestData(cls):
        cls.customer_1 = create_customer({
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john.doe@gmail.com',
            'password': '*****',
            'address': 'Trg Dositeja Obradovića 6',
            'city': 'Novi Sad',
            'zipcode': '21000',
        })
        cls.customer_2 = create_customer({
            'firstname': 'Mary',
            'lastname': 'Jane',
            'email': 'mary.jane@gmail.com',
            'password': '*****',
            'address': 'Trg Dositeja Obradovića 6',
            'city': 'Novi Sad',
            'zipcode': '21000',
        })

    def test_unauthenticated(self):
        c = Client()
        response = c.post('/api/register/', data=self.good_request, content_type='application/json')
        self.assertEquals(response.status_code, 200)

    def test_wrong_method(self):
        c = Client()
        response = c.get('/api/register/')
        self.assertEquals(response.status_code, 405)

    def test_missing_field(self):
        c = Client()
        response = c.post('/api/register/', data=self.bad_request_missing_field, content_type='application/json')
        self.assertEquals(response.status_code, 400)

    def test_bad_email(self):
        c = Client()
        response = c.post('/api/register/', data=self.bad_request_bad_email, content_type='application/json')
        self.assertEquals(response.status_code, 400)

    def test_empty_field(self):
        c = Client()
        response = c.post('/api/register/', data=self.bad_request_empty_field, content_type='application/json')
        self.assertEquals(response.status_code, 400)

    def test_registration_must_return_activation_link(self):
        c = Client()
        response = c.post('/api/register/', data=self.good_request, content_type='application/json')
        try:
            activation_link = response.data['activation_link']
            self.assertEquals(response.status_code, 200)
        except KeyError:
            self.fail('activation_link not found in response')

    def test_registration_login_successful(self):
        c = Client()
        response = c.post('/api/register/', data=self.good_request, content_type='application/json')
        activation_link = response.data['activation_link']
        response = c.get(f'/activate/{activation_link}/')
        self.assertEquals(response.status_code, 200)
        status, token, customer_id = authenticate(self, c, self.good_request['email'], self.good_request['password'])
        self.assertEquals(status, 200)
        response = c.get(f'/api/customers/{customer_id}/', HTTP_AUTHORIZATION=f'JWT {token}')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['id'], customer_id)

    def test_login_fails_with_wrong_password(self):
        c = Client()
        status, token, customer_id = authenticate(self, c, self.customer_1.user.email, '6adP4ssW0rd')
        self.assertEquals(status, 400)

    def test_cannot_login_without_activation(self):
        c = Client()
        response = c.post('/api/register/', data=self.good_request, content_type='application/json')
        status, token, customer_id = authenticate(self, c, self.good_request['email'], self.good_request['password'])
        self.assertNotEquals(status, 200)

    def test_not_allowed_to_read_another_customer(self):
        c = Client()
        status_1, token_1, customer_id_1 = authenticate(self, c, self.customer_1.user.email, self.customer_1.password)
        self.assertEquals(status_1, 200)
        status_2, token_2, customer_id_2 = authenticate(self, c, self.customer_2.user.email, self.customer_2.password)
        self.assertEquals(status_1, 200)

        # try to read data on customer #2 while logged in as customer #1
        response = c.get(f'/api/customers/{customer_id_2}/', HTTP_AUTHORIZATION=f'JWT {token_1}')
        self.assertEquals(response.status_code, 403)

    def not_now_test_register_throttle(self):
        c = Client()
        request_count = 1
        while True:
            data = self.good_request.copy()
            data['email'] = f"johnny.doe.{request_count}@gmail.com"
            response = c.post('/api/register/', data=data, content_type='application/json')
            if response.status_code != 200:
                break
            request_count += 1
        self.assertLessEqual(request_count, settings.API_THROTTLE_RATE)


def authenticate(test_case, client, username, password):
    """
    Pomocna funkcija za autentifikaciju
    :param test_case: Django test case koji koristi ovu funkciju
    :param client: Django test client
    :param username: email za login
    :param password: lozinka za login
    :return: tuple (http status code, JWT token, customer id)
    """
    response = client.post('/api/token-auth/', {'username': username, 'password': password})
    if response.status_code != 200:
        return response.status_code, None, None
    try:
        token = response.data['token']
        customer_id = response.data['id']
        return response.status_code, token, customer_id
    except KeyError:
        test_case.fail('token not found in auth response')


def create_customer(data):
    user = User.objects.create_user(data['email'], data['email'], data['password'], is_staff=0, is_active=1)
    user.first_name = data['firstname']
    user.last_name = data['lastname']
    user.save()
    customer = Customer.objects.create(user=user, address=data['address'], city=data['city'], zip_code=data['zipcode'])
    customer.password = data['password']
    return customer


