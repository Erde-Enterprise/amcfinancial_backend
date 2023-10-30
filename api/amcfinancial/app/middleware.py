from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import User_Root, Customer
import jwt
from amcfinancial.settings import SECRET_KEY

def teste_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user_type = payload['type']

        if user_type == 0:
            user = get_object_or_404(User_Root, id=user_id)
            return {'validity': True, 'id': user.id, 'type': 0}
        else:
            user = get_object_or_404(Customer, id=user_id)
            return {'validity': True, 'id': user.id, 'type': user.type}
    except jwt.ExpiredSignatureError:
        return {'validity': False}
    except jwt.exceptions.DecodeError:
        return {'validity': False}
    except Http404:
        return {'validity': False}
