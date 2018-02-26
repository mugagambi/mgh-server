from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from djoser import constants
from djoser.compat import get_user_email, get_user_email_field_name
from djoser.conf import settings
from rest_framework import serializers

from core import models

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            User.USERNAME_FIELD,
            'phone_number',
            'first_name',
            'last_name',
            'last_login'
        )
        read_only_fields = (User.USERNAME_FIELD,)

    def update(self, instance, validated_data):
        email_field = get_user_email_field_name(User)
        if settings.SEND_ACTIVATION_EMAIL and email_field in validated_data:
            instance_email = get_user_email(instance)
            if instance_email != validated_data[email_field]:
                instance.is_active = False
                instance.save(update_fields=['is_active'])
        return super(UserSerializer, self).update(instance, validated_data)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    default_error_messages = {
        'cannot_create_user': constants.CANNOT_CREATE_USER_ERROR,
    }

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD, User._meta.pk.name, 'password', 'phone_number',
            'first_name',
            'last_name',
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail('cannot_create_user')

        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.save(update_fields=['is_active'])
        return user


class AggregationCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AggregationCenter
        fields = ('id', 'name', 'location')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'name',)


class AggregationCenterProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AggregationCenterProduct
        fields = ('id', 'aggregation_center', 'product', 'active')


class CrateTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CrateType
        fields = ('id', 'name', 'weight')


class CrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Crate
        fields = ('id', 'number', 'type')
