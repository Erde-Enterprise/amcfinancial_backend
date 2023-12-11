from django.contrib.contenttypes.models import ContentType
import filetype

from geopy.geocoders import OpenCage
from geopy.exc import GeocoderTimedOut

from .models import User_Root, Customer, UserProfile
from amcfinancial.settings import OPENCAGE_API_KEY


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
        return None

def location_validation(latitude, longitude):
    geolocator = OpenCage(api_key=OPENCAGE_API_KEY)
    try:
        localization = geolocator.reverse((latitude, longitude), exactly_one=True)
        country = localization.raw['components']['country']
        if country == 'Brazil' or country == 'Brasil':
            return {'validation': True, 'country': country} 
        else:
            return {'validation': False, 'country': country} 
    except:
        return {'validation': False}

        
