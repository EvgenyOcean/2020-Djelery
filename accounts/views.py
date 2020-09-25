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
from .tasks import user_scraping



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
    Как только юзер вводит данные в profile, они приходят сюда
    и начинается парсинг контента; если удалось пройти habr
    authentication, тогда (mailname - это email or username зависит от сервиса)
    '''
    mailname = request.data['mailname']
    password = request.data['password']
    source = request.data['source']
    current_username = request.user.username
    task = user_scraping.delay(mailname, password, source, current_username)

    return Response({"task_id": task.task_id}, status=status.HTTP_202_ACCEPTED)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def task_check(request):
    '''
    AJAX реквесты, чтобы посмотреть что там по статусу задания, 
    и если что обновить UI/redirect туда куда нужно
    '''
    print(f'task_check got: {request.data["task_id"]}')
    task = app.AsyncResult(request.data['task_id'])
    task_status = task.status
    task_result = 'NOT DONE YET'
    if (task_status == 'SUCCESS'):
        task_result = task.get()
    print(f'task_check is sending: status: {task_status}; result: {task_result}')
    return Response({'status': task_status, 'result': task_result}, status=status.HTTP_200_OK)
