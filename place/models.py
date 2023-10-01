import uuid

from django.contrib.auth import get_user_model
from django.contrib.gis.db import models

from DigitalLurker.utils import uuid_upload_to

User = get_user_model()


class Place(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.TextField(max_length=64)
    description = models.TextField(max_length=256, null=True)
    main_image = models.ImageField(upload_to=uuid_upload_to('places'),
                                   default='defaults/places/default.png',
                                   blank=False,
                                   null=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.PointField(null=False, blank=False)
    is_active = models.BooleanField(default=True)
    experience = models.IntegerField()

    def __str__(self):
        return self.name


class PlacePhoto(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_place_photos')
    image = models.ImageField(upload_to=uuid_upload_to('place_photos'))
    title = models.CharField(max_length=64, null=False)
    description = models.CharField(max_length=256, null=False)

    def __str__(self):
        return f'{self.place.name} by {self.owner.username}'


class PlacePhotoLike(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    place_photo = models.ForeignKey(PlacePhoto, on_delete=models.CASCADE, related_name='likes')

    def __str__(self):
        return f'{self.place_photo.place.name} photo by {self.owner.username}'
