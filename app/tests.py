from unittest.mock import patch

from django.contrib.auth.models import User

from django.test import TestCase, RequestFactory
from django.test import Client

from app.models import Review, Event
from app.views import add_route_event


class TestReview(TestCase):
    def test_route_review(self):
        client = Client()
        response = client.get('/app/review')
        self.assertEqual(200, response.status_code)

    def test_add_review(self):
        review = Review(
            route_id=1,
            review='ololosha',
            review_rate=5
        )
        review.save()
        client = Client()
        response = client.post('/app/review', {'route_id': 1})
        self.assertEqual(200, response.status_code)


class TestRoute(TestCase):

    def test_filter_route(self):
        client = Client()
        response = client.get('/app/<route_type>')
        self.assertEqual(200, response.status_code)

    def test_filter_route1(self):
        client = Client()
        route_type = 'car'
        response = client.get(f'/app/{route_type}')
        self.assertEqual(200, response.status_code)

    def test_filter_route2(self):
        client = Client()
        route_type = 'car'
        country = 'Ukraine'
        response = client.get(f'/app/{route_type}/{country}')
        self.assertEqual(200, response.status_code)

    def test_filter_route3(self):
        client = Client()
        route_type = 'car'
        country = 'Ukraine'
        location = 'kyiv'
        response = client.get(f'/app/{route_type}/{country}/{location}')
        self.assertEqual(200, response.status_code)


class TestEvent(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        class UserMock:
            def has_perm(self, *args, **kwargs):
                return True

        self.user = UserMock()

    def test_anonymous_user(self):
        client = Client()
        response = client.get('/app/1/add_event')
        self.assertEqual(401, response.status_code)
        # Нужно закоментить рядок 106 views.py, который делает откат на /login

        response_client_post = client.post('/app/1/add_event')
        self.assertEqual(401, response_client_post.status_code)

    def test_with_user(self):
        request = self.factory.post('/app/1/add_event', {'id_route': 1, 'start_date': "2022-12-13", 'price': 488})
        request.user = self.user

        response = add_route_event(request, id_route=1)
        self.assertEqual(response.status_code, 200)

        itms = list(Event.objects.all().filter(price=488))
        self.assertEqual(1, itms[0].id_route)
