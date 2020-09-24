from django.shortcuts import render, redirect, get_object_or_404
from .models import Post

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PostsSerializer

from .tasks import start_scraping, get_full_content


# Create your views here.
def home(request):    
    return render(request, 'posts/home.html', {})

def detailed(request, pk):
    # DONT FORGET TO MIGRATE
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'posts/detailed.html', {'post': post})

def initla_scrap(request):
    start_scraping.delay()
    # I gotta send cookies saying something like:
    # "Yo, chill data is on its way"
    # Then JS checks cookie, if its there make every 10sec request
    # to the check task status API, once response is good
    # JS refreshes the page with updated posts
    return redirect(home)
    

# API VIEWS
@api_view(['POST'])
def get_featured_posts(request):
    # request.data and check for chosen sources
    try:
        featured_posts = Post.objects.featured(request.data['sources'])
        serializer = PostsSerializer(featured_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except: 
        return Response({"message": "Source does not exist!"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_content(request):
    try:
        post_id = request.data['post_id']
        Post.objects.get(id=post_id)
        task = get_full_content.delay(post_id)

        return Response({'task_id': task.task_id}, status=status.HTTP_200_OK)

    except:
        return Response({"message": "Post does not exist!"})