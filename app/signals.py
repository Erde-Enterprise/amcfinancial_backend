from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from .models import User_Root
import os

@receiver(post_migrate)
def create_user_root(sender, **kwargs):
    if User_Root.objects.count() == 0:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        avatar_path = os.path.join(current_directory, 'static/images/avatar.png')
        
        with open(avatar_path, 'rb') as f:
            imagem_bytes = f.read()
        User_Root.objects.create(
            email_root='root@gmail.com',
            password= make_password('root12345'),
            nickname='root',
            name='Admin',
            photo=imagem_bytes
        )

def create_user_root2():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    avatar_path = os.path.join(current_directory, 'static/images/avatar.png')
    with open(avatar_path, 'rb') as f:
        imagem_bytes = f.read()
    User_Root.objects.create(
        email_root='root2@gmail.com',
        password= make_password('root123456'),
        nickname='root2',
        name='Admin2',
        photo=imagem_bytes
    )