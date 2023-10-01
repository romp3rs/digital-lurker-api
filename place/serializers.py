from math import floor

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry, GEOSException
from geopy.distance import distance
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from place.models import Place, PlacePhoto, PlacePhotoLike
from user.serializers import UserSerializer

User = get_user_model()


class PlaceSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ['public_id',
                  'name',
                  'main_image',
                  'location',
                  'added_by',
                  'distance',
                  'experience',
                  'description']
        extra_kwargs = {'added_by': {'write_only': True}}

    def get_distance(self, obj):
        point = self.context['request'].headers.get('Point')
        if point is None:
            return 0

        try:
            point_location = GEOSGeometry(point)
        except GEOSException:
            raise ValidationError(_('Wrong localization format. Use POINT(x y). '))

        return floor(distance(obj.location, point_location).meters)


class PlacePhotoSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    place = PlaceSerializer(read_only=True)

    liked = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = PlacePhoto
        fields = ['public_id',
                  'owner',
                  'place',
                  'image',
                  'title',
                  'liked',
                  'like_count',
                  'description']
        extra_kwargs = {'image': {'read_only': True}}

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_liked(self, obj):
        request = self.context.get('request')

        if request.user is not None:
            return PlacePhotoLike.objects.filter(owner=request.user, place_photo=obj).exists()
        return False


class CreatePlacePhotoSerializer(PlacePhotoSerializer):
    place_pk = serializers.SlugRelatedField(
        source='place', queryset=Place.objects.all(), slug_field='pk', write_only=True
    )

    owner_pk = serializers.SlugRelatedField(
        source='owner', queryset=User.objects.all(), slug_field='pk', write_only=True
    )

    class Meta:
        model = PlacePhoto
        fields = ['public_id',
                  'place',
                  'place_pk',
                  'owner',
                  'owner_pk',
                  'image',
                  'title',
                  'like_count']


class PlacePhotoLikeSerializer(serializers.ModelSerializer):
    owner_pk = serializers.SlugRelatedField(
        source='owner', queryset=User.objects.all(), slug_field='pk', write_only=True
    )
    place_photo_pk = serializers.SlugRelatedField(
        source='place_photo', queryset=PlacePhoto.objects.all(), slug_field='pk', write_only=True
    )

    class Meta:
        model = PlacePhotoLike
        fields = ['owner_pk', 'place_photo_pk']
