from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from posts.models import Post
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegisterFrom

from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from djelery.celery import app
from posts.tasks import user_scraping



# Create your views here.
@login_required
def profile(request):
    return render(request, 'accounts/account.html', {})

def register(request):
    if request.user.is_authenticated: 
        return redirect('home')
    if request.method == 'POST':
        form = UserRegisterFrom(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account for {username} has been created! You can log in!')
            return redirect('/login')
    else: 
        form = UserRegisterFrom()
    return render(request, 'accounts/register.html', {'form': form})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_credentials(request):
    '''
    Once user enters credentials on a profile page, it comes right here
    and parsing starts; if habr login successfull then 
    (mailname - is mail or username depending on a server)
    '''
    mailname = request.data['mailname']
    password = request.data['password']
    # need to verify source
    source = request.data['source']
    username = request.user.username
    task = user_scraping.delay(password, mailname, source, username)

    return Response({"task_id": task.task_id}, status=status.HTTP_202_ACCEPTED)

@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def task_check(request):
    '''
    AJAX requests to check the task status
    and accordingly update the UI
    '''
    print(f'task_check got: {request.data["task_id"]}')
    task = app.AsyncResult(request.data['task_id'])
    task_status = task.status
    task_result = 'NOT DONE YET'
    if (task_status == 'SUCCESS'):
        task_result = task.get()
    print(f'task_check is sending: status: {task_status}; result: {task_result}')
    return Response({'status': task_status, 'result': task_result}, status=status.HTTP_200_OK)
