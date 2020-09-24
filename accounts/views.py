from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from posts.models import Post
from django.contrib.auth.models import User


from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .tasks import user_scraping



# Create your views here.
@login_required
def profile(request):
    return render(request, 'accounts/account.html', {})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_credentials(request):
    #I wanna get: 
    #service and credintials for that service
    #and go for scraping
    #I wanna return: 
    #selery task ID to track the status
    # <QueryDict: {'source': ['vc'], 'email': ['evgeny.ocean@gmail.com'], 'password': ['fsdafas']}>
    mailname = request.data['mailname']
    password = request.data['password']
    source = request.data['source']
    current_username = request.user.username
    user_scraping.delay(mailname, password, source, current_username)

    return Response({"message": "all good"}, status=status.HTTP_202_ACCEPTED)