from django.urls import path
from .views import verify_credentials, task_check

app_name = "accounts"
urlpatterns = [
  path('verify_credentials/', verify_credentials, name="verifier"),
  path('task_check/', task_check, name="checker"),
]