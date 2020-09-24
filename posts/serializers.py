from rest_framework import serializers
from django.conf import settings
from .models import Post

class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post 
        fields = ['id', 'title', 'content', 'link']