from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from posts.views import home, initla_scrap

urlpatterns = [
    path('', home, name="home"),
    path('init-scrap/', initla_scrap, name="init"),
    path('api/posts/', include('posts.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
