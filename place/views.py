from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import Distance
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from django.contrib.auth import get_user_model

from .models import Place, PlacePhoto, PlacePhotoLike
from .serializers import PlaceSerializer, PlacePhotoSerializer, PlacePhotoLikeSerializer, CreatePlacePhotoSerializer

User = get_user_model()


class PlaceViewSet(viewsets.ModelViewSet):
    lookup_field = 'public_id'
    queryset = Place.objects.all().order_by('id')
    serializer_class = PlaceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a new place.
        """
        serializer = self.get_serializer(data=request.data | {'added_by': request.user.pk})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves information for a place specified by public_id.
        """
        user = self.get_object()

        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        Lists places information.
        """
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Handles the updating of the place's information.
        """
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Handles partial updating of the place's information.
        """
        place = self.get_object()
        serializer = self.get_serializer(place, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Handles deletion of the place.
        """
        place = self.get_object()

        if place.added_by != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        self.perform_destroy(place)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def filter_queryset(self, queryset):
        place_range = self.request.query_params.get('range')
        if place_range is not None:
            point = self.request.headers.get('Point')
            if point is None:
                raise ValidationError({"msg": "Point header is missing."})

            location = GEOSGeometry(point)
            queryset = queryset.filter(
                location__distance_lt=(location, Distance(m=place_range))
            )

        return super().filter_queryset(queryset)


class PlacePhotoViewSet(viewsets.ModelViewSet):
    lookup_field = 'public_id'
    queryset = PlacePhoto.objects.all().order_by('id')
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a new place photo.
        """
        if self.kwargs.get('place_public_id') is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        place = Place.objects.filter(public_id=self.kwargs.get('place_public_id')).first()

        if place is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not place.is_active:
            return Response(_('You can not add photo for a place that is not active'),
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(
            data=request.data.dict() | {'place_pk': place.pk,
                                        'image': request.FILES.get('image'),
                                        'owner_pk': request.user.id})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a place photo.
        """
        photo = self.get_object()

        if photo is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(photo)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def retrieve_mine(self, request, *args, **kwargs):
        """
        Retrieves information of a place of a user.
        """
        serializer = self.get_serializer(request.user.my_place_photos)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Handles partial updating of the place's photo information.
        """
        place = self.get_object()
        serializer = self.get_serializer(place, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        Lists photos of a place.
        """
        place = get_object_or_404(Place, public_id=self.kwargs.get('place_public_id'))
        queryset = self.filter_queryset(self.get_queryset()).filter(place__id=place.id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Handles deletion of the place photo.
        """
        photo = self.get_object()

        if photo.owner != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        self.perform_destroy(photo)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePlacePhotoSerializer
        return PlacePhotoSerializer


class PlacePhotoLikeViewSet(viewsets.ModelViewSet):
    queryset = PlacePhotoLike.objects.all().order_by('id')
    serializer_class = PlacePhotoLikeSerializer

    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a new place.
        """
        place_photo = get_object_or_404(PlacePhoto, public_id=self.kwargs.get('photo_public_id'))

        if self.get_queryset().filter(owner=request.user, place_photo=place_photo).exists():
            return Response(_('You can not like the same photo twice. '), status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={'owner_pk': request.user.id, 'place_photo_pk': place_photo.pk})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a place photo like.
        """
        return Response({'exists': self.get_queryset().filter(owner=request.user).exists()})

    def destroy(self, request, *args, **kwargs):
        """
        Handles deletion of the place's like.
        """

        like = self.get_object()

        if like is None:
            return Response('You have to like the photo first. ', status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(like)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        return self.get_queryset().filter(place_photo__public_id=self.kwargs.get('photo_public_id'), owner=self.request.user)
