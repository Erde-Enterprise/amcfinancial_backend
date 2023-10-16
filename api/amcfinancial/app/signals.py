from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import User_Root

@receiver(post_migrate)
def create_user_root(sender, **kwargs):
    if User_Root.objects.count() == 0:
        User_Root.objects.create(
            email_Root='root@gmail.com',
            password='root12345',
        )
