from django.urls import path
from .views import verify_credentials

app_name = "accounts"
urlpatterns = [
  path('verify_credentials/', verify_credentials, name="verifier"),
]