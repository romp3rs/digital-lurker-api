from django.contrib import admin

from place.models import PlacePhoto, Place, PlacePhotoLike

# Register your models here.
admin.site.register(Place)
admin.site.register(PlacePhoto)
admin.site.register(PlacePhotoLike)
