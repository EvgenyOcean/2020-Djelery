from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Post

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .serializers import PostsSerializer

from .tasks import scrap_top_posts, get_full_content

# VIEWS I WANNA SEE HERE: 
# home, detailed, feed are okay, cuz they render templates for three main pages

# APIs I WANNA SEE HERE: 
# get_featured_posts, get_users_post, get_content



# User Feed Paginator
def get_paginated_qs_response(qs, request):
    paginator = PageNumberPagination()
    paginator.page_size = 15
    paginated_qs = paginator.paginate_queryset(qs, request)
    seriazlier = PostsSerializer(paginated_qs, many=True)
    return paginator.get_paginated_response(seriazlier.data)


def home(request):    
    return render(request, 'posts/home.html', {})

# MAIN VIEW FOR DETAILED POST
def detailed(request, pk):
    # DONT FORGET TO MIGRATE
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'posts/detailed.html', {'post': post})


# MAIN VIEW FOR USER FEED
def feed(request, username):
    # I'm not sure I want users to check
    # other user's feed
    if username != request.user.username: 
        return redirect('home')
    user = get_object_or_404(User, username=username) #redundant one
    users_post = user.posts.all()
    return render(request, 'posts/feed.html', {'posts': users_post})

# EMULATING INITIAL SCRAPING
# JUST FOR TESTING PURPOSES
# CUZ TOP POSTS SCRAPING MUST BE RUN ACCRORDING TO THE SCHEDULE!
@api_view(['GET'])
def initial_scrap(request):
    # that's some sort of entrypoint for initial scraping
    task = scrap_top_posts.delay('habr')
    task2 = scrap_top_posts.delay('vc')
    # IMPLEMENT USER NOTIFIER!
    return Response({'task_id': [task.task_id, task2.task_id]}, status=status.HTTP_200_OK)
    


@api_view(['POST'])
def get_featured_posts(request):
    '''
    Send all the articles form habr/top
    To populate home page
    '''
    # request.data and check for chosen sources
    try:
        featured_posts = Post.objects.featured(request.data['sources'])
        serializer = PostsSerializer(featured_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except: 
        return Response({"message": "Source does not exist!"}, status=status.HTTP_200_OK)


# API VIEWS
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_users_post(request):
    '''
    Send only user-specific articles
    '''
    username = request.data['username']
    if username != request.user.username: 
        print('Not authorized')
        return Response({"message": "Not authorized!"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        print('Everything is smooth!')
        sources = request.data['sources']
        user = User.objects.filter(username=username).first()
        users_post = user.posts.filter(source__in=sources)
        return get_paginated_qs_response(users_post, request)
        # return Response(serializer.data, status=status.HTTP_200_OK)
    except: 
        # gotta look up a correct status
        return Response({"message": "Something went wrong!"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def get_content(request):
    '''
    Loads complete article text
    '''
    try:
        post_id = request.data['post_id']
        Post.objects.get(id=post_id)
        task = get_full_content.delay(post_id)

        return Response({'task_id': task.task_id}, status=status.HTTP_200_OK)

    except:
        return Response({"message": "Post does not exist!"})

