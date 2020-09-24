from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    habr_email = models.EmailField(unique=True)
    habr_pass = models.CharField(max_length=250)
    vs_email = models.EmailField(unique=True)
    vc_pass = models.CharField(max_length=250)

    def __str__(self):
      representation = f'{self.user.username} Profile'
      return representation

def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_or_update_profile, sender=User)