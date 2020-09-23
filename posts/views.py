from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Post
from .serializers import PostsSerializer

# Create your views here.
def home(request):    
    return render(request, 'posts/home.html', {})


# API VIEWS
@api_view(['POST'])
def get_featured_posts(request):
    # request.data and check for chosen sources
    featured_posts = Post.objects.featured()
    serializer = PostsSerializer(featured_posts, many=True)
    
    return render(request, 'posts/home.html', {})
