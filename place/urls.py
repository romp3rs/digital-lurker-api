from django.urls import path

from .views import PlaceViewSet, PlacePhotoViewSet, PlacePhotoLikeViewSet

urlpatterns = [
    path('', PlaceViewSet.as_view({'post': 'create'})),

    path('search/', PlaceViewSet.as_view({'get': 'list'})),
    path('<uuid:public_id>/', PlaceViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'})),

    path('<uuid:place_public_id>/photos/', PlacePhotoViewSet.as_view({'get': 'list',
                                                                      'post': 'create'})),
    path('<uuid:place_public_id>/photos/<uuid:public_id>/', PlacePhotoViewSet.as_view({'get': 'retrieve',
                                                                                       'patch': 'partial_update',
                                                                                       'delete': 'destroy'})),

    path('<uuid:place_public_id>/photos/<uuid:photo_public_id>/likes/',
         PlacePhotoLikeViewSet.as_view({'post': 'create',
                                        'get': 'retrieve',
                                        'delete': 'destroy'}))
]
