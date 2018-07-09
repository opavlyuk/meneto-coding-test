from flask import Flask

from src.settings import BASKET_API_URL
from src.views import BasketAPI
from src.url_helpers import register_api

app = Flask(__name__)
register_api(app, BasketAPI, 'basket_api', BASKET_API_URL, pk='basket_id')
