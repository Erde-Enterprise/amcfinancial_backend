from .models import User_Root, Customer, UserProfile
from django.contrib.contenttypes.models import ContentType
def user_profile_type(validation):
    if validation['type'] == 0:
        user = UserProfile.objects.create(
            content_type= ContentType.objects.get_for_model(User_Root),
            object_id= validation['id'],
        )
        user.save()
        return user
    else:
        user = UserProfile.objects.create(
            content_type= ContentType.objects.get_for_model(Customer),
            object_id= validation['id'],
        )
        user.save()
        return user
