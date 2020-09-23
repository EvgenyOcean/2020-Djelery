from django.shortcuts import render, redirect
from .models import Post

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PostsSerializer

from .tasks import start_scraping


# Create your views here.
def home(request):    
    return render(request, 'posts/home.html', {})

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
    featured_posts = Post.objects.featured(request.data['sources'])
    serializer = PostsSerializer(featured_posts, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

