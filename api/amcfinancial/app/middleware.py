from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import User_Root, Customer
import jwt
from amcfinancial.settings import SECRET_KEY

def teste_token(header):
    try:
        autorization_header = header.get('Authorization', None)
        if autorization_header:
            parts = autorization_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':   
                token = parts[1]             
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                user_id = payload['user_id']
                user_type = payload['type']

                if user_type == 0:
                    user = get_object_or_404(User_Root, id=user_id)
                    return {'validity': True, 'id': user.id, 'type': 0}
                else:
                    user = get_object_or_404(Customer, id=user_id)
                    return {'validity': True, 'id': user.id, 'type': user.type}
            else:
                return {'validity': False}      
        else:
            return {'validity': False}
    except:
        return {'validity': False}
        
