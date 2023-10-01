from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Place, PlacePhoto, PlacePhotoLike

User = get_user_model()


class PlaceViewSetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(email='admin@admin.com',
                                                  username='testuser',
                                                  password='testpass',
                                                  date_of_birth='2001-01-01')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_place_not_admin(self):
        not_admin_user = User.objects.create_user(email='admintwo@admin.com',
                                                  username='testusertwo',
                                                  password='testpasstwo',
                                                  date_of_birth='2001-01-01')
        self.client.force_authenticate(user=not_admin_user)

        data = {
            "name": "Test Place",
            "location": "POINT(1.234 5.678)",
            "experience": 30
        }
        response = self.client.post('/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Place.objects.count(), 0)

    def test_create_place(self):
        data = {
            "name": "Test Place",
            "location": "POINT(1.234 5.678)",
            "experience": 30
        }
        response = self.client.post('/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Place.objects.count(), 1)
        self.assertEqual(Place.objects.get().name, 'Test Place')

    def test_retrieve_place(self):
        place = Place.objects.create(name='Test Place',
                                     location='POINT(1.234 5.678)',
                                     added_by=self.user,
                                     experience=40)
        response = self.client.get(f'/places/{place.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Place')

    def test_update_place(self):
        place = Place.objects.create(name='Test Place',
                                     location='POINT(1.234 5.678)',
                                     added_by=self.user,
                                     experience=40)

        data = {
            "name": "Test Update Place",
            "location": "POINT(9 7)",
        }

        response = self.client.patch(f'/places/{place.public_id}/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Update Place')
        self.assertEqual(response.data['location'], 'SRID=4326;POINT (9 7)')
        self.assertEqual(response.data['experience'], 40)

    def test_destroy_place(self):
        place = Place.objects.create(name='Test Place',
                                     location='POINT(1.234 5.678)',
                                     added_by=self.user,
                                     experience=40)

        response = self.client.delete(f'/places/{place.public_id}/', format='json', redirect=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Place.objects.all().count(), 0)


class PlacePhotoTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(email='admin@admin.com',
                                                  username='testuser',
                                                  password='testpass',
                                                  date_of_birth='2001-01-01')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_place_photo(self):
        place = Place.objects.create(name='Test Place',
                                     location='POINT(1.234 5.678)',
                                     added_by=self.user,
                                     experience=40)

        data = {
            "title": "Title",
            "image": open('./media/defaults/pfps/default.png', 'rb')
        }

        response = self.client.post(f'/places/{place.public_id}/photos/',
                                    data=data,
                                    format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PlacePhoto.objects.count(), 1)
        self.assertEqual(PlacePhoto.objects.get().title, 'Title')

    def test_retrieve_place_photo(self):
        place = Place.objects.create(name='Test Place',
                                     location='POINT(1.234 5.678)',
                                     added_by=self.user,
                                     experience=40)
        response = self.client.get(f'/places/{place.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Place')

    def test_update_place_photo(self):
        place = Place.objects.create(name='Test Place',
                                     location='POINT(1.234 5.678)',
                                     added_by=self.user,
                                     experience=40)

        place_photo = PlacePhoto.objects.create(owner=self.user,
                                                place=place,
                                                title='Old title')

        data = {
            "title": "New title",
        }

        response = self.client.patch(f'/places/{place.public_id}/photos/{place_photo.public_id}/',
                                     data=data,
                                     format='json',
                                     follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PlacePhoto.objects.all()[0].title, 'New title')

    def test_destroy_place(self):
        place = Place.objects.create(name='Test Place',
                                     location='POINT(1.234 5.678)',
                                     added_by=self.user,
                                     experience=40)

        place_photo = PlacePhoto.objects.create(owner=self.user,
                                                place=place,
                                                title='title')

        response = self.client.delete(f'/places/{place.public_id}/photos/{place_photo.public_id}/',
                                      format='json',
                                      redirect=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PlacePhoto.objects.all().count(), 0)


class PlacePhotoLikeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(email='admin@admin.com',
                                                  username='testuser',
                                                  password='testpass',
                                                  date_of_birth='2001-01-01')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_place_photo_like(self):
        place = Place.objects.create(name='Test Place',
                                     location='POINT(1.234 5.678)',
                                     added_by=self.user,
                                     experience=40)

        place_photo = PlacePhoto.objects.create(owner=self.user,
                                                place=place,
                                                title='title')

        response = self.client.get(f'/places/{place.public_id}/photos/{place_photo.public_id}/')
        self.assertFalse(response.data.get('liked'))

        response = self.client.post(f'/places/{place.public_id}/photos/{place_photo.public_id}/likes/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PlacePhotoLike.objects.count(), 1)
        self.assertEqual(place_photo.likes.all().count(), 1)

        response = self.client.post(f'/places/{place.public_id}/photos/{place_photo.public_id}/likes/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PlacePhotoLike.objects.count(), 1)
        self.assertEqual(place_photo.likes.all().count(), 1)

        response = self.client.get(f'/places/{place.public_id}/photos/{place_photo.public_id}/')
        self.assertTrue(response.data.get('liked'))

    def test_destroy_place(self):
        place = Place.objects.create(name='Test Place',
                                     location='POINT(1.234 5.678)',
                                     added_by=self.user,
                                     experience=40)

        place_photo = PlacePhoto.objects.create(owner=self.user,
                                                place=place,
                                                title='title')

        place_photo_like = PlacePhotoLike.objects.create(place_photo=place_photo,
                                                         owner=self.user)

        response = self.client.delete(f'/places/{place.public_id}/photos/{place_photo.public_id}/likes/',
                                      format='json',
                                      redirect=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PlacePhotoLike.objects.all().count(), 0)
        self.assertEqual(place_photo.likes.all().count(), 0)
