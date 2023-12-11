from django.test import TestCase

# Create your tests here.

from geopy.geocoders import OpenCage
from geopy.exc import GeocoderTimedOut


def obter_pais(latitude, longitude, chave_api_opencage):
    geolocator = OpenCage(api_key=chave_api_opencage)

    try:
        localizacao = geolocator.reverse((latitude, longitude), exactly_one=True)
        pais = localizacao.raw['components']['country']
        return pais

    except GeocoderTimedOut:
        return "Erro: O servidor de geocodificação demorou para responder."
    except:
        return "Erro: O serviço de geocodificação está indiscente."

# Exemplo de uso da função
latitude = -1.265
longitude =  -38.9556
chave_api_opencage = '3ecba9e0adc6446c8ea00258c571de24'
pais = obter_pais(latitude, longitude, chave_api_opencage)
print(pais)
