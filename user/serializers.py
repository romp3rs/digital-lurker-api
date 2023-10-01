import datetime
from uuid import uuid4

from PIL import Image
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Sum, F
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
from rest_framework.validators import UniqueValidator

from place.models import Place, PlacePhoto

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    total_experience = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['public_id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'date_of_birth',
                  'pfp',
                  'total_experience',
                  'password']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
        user = super().save(**kwargs)

        if user.pfp.name != user.pfp.field.default:
            image = Image.open(user.pfp)
            resized_image = image.resize((256, 256), Image.ANTIALIAS)
            resized_image.save(user.pfp.path)

        return user

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('password') is not None:
            validated_data['password'] = make_password(validated_data['password'])

        return super().update(instance, validated_data)

    def validate_password(self, password):
        validate_password(password)
        return password

    def validate_date_of_birth(self, date_of_birth):
        if datetime.date.today() - date_of_birth < datetime.timedelta(days=18 * 365):
            raise serializers.ValidationError(_('The user must be an adult. '))
        return date_of_birth

    def get_total_experience(self, obj):
        exp = 0

        for place in Place.objects.filter(placephoto__owner=obj).distinct():
            exp += place.experience

        return exp


class CreateUserSerializer(UserSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(User.objects.all())])
    username = serializers.CharField(max_length=150,
                                     validators=[UniqueValidator(User.objects.all())])

    class Meta:
        model = User
        fields = ['public_id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'date_of_birth',
                  'pfp',
                  'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'read_only': False},
            'email': {'read_only': False}
        }


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['public_id', 'username', 'first_name', 'last_name', 'date_of_birth', 'pfp']
        read_only_fields = ('public_id', 'first_name', 'last_name', 'date_of_birth', 'pfp')
