from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
  path('featured/', views.get_featured_posts, name='home'),
]