from .models import User_Root, Customer
from .serializers import AccessSerializer
import jwt


import sys
sys.path.append('..')
from amcfinancial.settings import SECRET_KEY

def teste_token(request):
    try:
        serialize = AccessSerializer(data=request)
        serialize.is_valid(raise_exception=True)
        token = serialize.validated_data['access_token']
        payload = jwt.decode(token,SECRET_KEY, algorithms=['HS256'])
        user = User_Root.objects.get(id=payload['user_id'])
        if user:
            return {'validity': True, 'id': user.id, 'type': 0}
        else:
            user = Customer.objects.get(id=payload['user_id'])
            if user:
                return {'validity': True, 'id': user.id, 'type': user.type_user}
            else:
                return {'validity': False}
    except jwt.ExpiredSignatureError as identifier:
            return {'validity': False}
    except jwt.exceptions.DecodeError as identifier:
             return {'validity': False}