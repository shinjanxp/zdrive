from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.conf import settings
import os
from rest_framework.validators import UniqueValidator
ZDRIVE_ROOT = settings.ZDRIVE_ROOT

class DirectorySerializer(serializers.Serializer):
	name = serializers.CharField(max_length=255)
	path = serializers.FilePathField(path=ZDRIVE_ROOT,recursive=True)

	def create(self, validated_data):
		"""
		Create and return a new `Snippet` instance, given the validated data.
		"""
		return Directory.objects.create(**validated_data)

	def update(self, instance, validated_data):
		"""
		Update and return an existing `Snippet` instance, given the validated data.
		"""
		instance.name = validated_data.get('name', instance.name)
		instance.path = validated_data.get('path', instance.path)
		instance.save()
		return instance	

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    username = serializers.CharField(
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(min_length=8,write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'],
             validated_data['password'])
        # Create user's root directory same as username
        abs_path = os.path.join(ZDRIVE_ROOT, user.username)
        if not os.path.exists(abs_path):
        	os.makedirs(abs_path)
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')