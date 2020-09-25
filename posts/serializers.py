from rest_framework import serializers
from django.conf import settings
from .models import Post

class PostsSerializer(serializers.ModelSerializer):
    '''
    Принимает посты => сериализует => that's all she wrote
    '''
    class Meta:
        model = Post 
        fields = ['id', 'title', 'content', 'link']