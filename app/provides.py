from .models import User_Root, Customer, UserProfile
from django.contrib.contenttypes.models import ContentType
import filetype

def user_profile_type(validation):
    if validation['type'] == 0:
        user_profiles = UserProfile.objects.filter(content_type=ContentType.objects.get_for_model(User_Root), object_id=validation['id']).first()
        if user_profiles:
            return user_profiles
        else:
            user_profiles = UserProfile.objects.create(
                content_type= ContentType.objects.get_for_model(User_Root),
                object_id= validation['id'],
            )
            user_profiles.save()
            return user_profiles
    else:
        user_profiles = UserProfile.objects.filter(content_type=ContentType.objects.get_for_model(Customer), object_id=validation['id']).first()
        if user_profiles:    
            return user_profiles
        else:
            user_profiles = UserProfile.objects.create(
                content_type= ContentType.objects.get_for_model(Customer),
                object_id= validation['id'],
            )
            user_profiles.save()
        return user_profiles

def get_file_mime_type(file):
    try:
        kind = filetype.guess(bytearray(file))
        if kind is not None:
            return kind.mime
        else:
            return None
    except Exception as e:
        print(e)
        
