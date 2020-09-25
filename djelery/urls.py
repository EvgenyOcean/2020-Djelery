from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from posts.views import home, initial_scrap, detailed, feed
from accounts.views import profile, register

urlpatterns = [
    path('', home, name="home"),
    path('feed/<str:username>', feed, name='feed'),
    path('posts/<int:pk>/', detailed, name='detailed'),
    path('profile/', profile, name='profile'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name="accounts/login.html", redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('init-scrap/', initial_scrap, name="init"),
    path('api/posts/', include('posts.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
