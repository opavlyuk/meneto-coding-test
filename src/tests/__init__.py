import datetime
import unittest

from pony import orm

from src.settings import BASKET_API_URL
from src import app
from src.entities import db, Basket, BasketItem, Customer, Product


class BaseCase(unittest.TestCase):
    @orm.db_session
    def populate_db(self):
        self.customer_data = [
            {'name': 'Jon', 'has_loyalty': True, 'created': datetime.datetime.now()},
            {'name': 'Ramsay', 'has_loyalty': False, 'created': datetime.datetime.now()}
        ]
        self.customers = [Customer(**i) for i in self.customer_data]
        self.product_data = [
            {'title': 'Dragon', 'price': 10 ** 7, 'created': datetime.datetime.now()},
            {'title': 'Dog', 'price': 10 ** 1, 'created': datetime.datetime.now()}
        ]
        self.products = [Product(**i) for i in self.product_data]
        self.basket_data = [
            {'customer': self.customers[0], 'created': datetime.datetime.now()},
            {'customer': self.customers[1], 'created': datetime.datetime.now()}
        ]
        self.baskets = [Basket(**i) for i in self.basket_data]
        self.basket_items_data = [
            {'product': self.products[0], 'basket': self.baskets[0],
             'quantity': 3, 'created': datetime.datetime.now()},
            {'product': self.products[1], 'basket': self.baskets[0],
             'quantity': 4, 'created': datetime.datetime.now()},
            {'product': self.products[0], 'basket': self.baskets[0],
             'quantity': 1, 'created': datetime.datetime.now()},
            {'product': self.products[1], 'basket': self.baskets[0],
             'quantity': 1, 'created': datetime.datetime.now()},
            {'product': self.products[1], 'basket': self.baskets[1],
             'quantity': 5, 'created': datetime.datetime.now()},
            {'product': self.products[1], 'basket': self.baskets[1],
             'quantity': 1, 'created': datetime.datetime.now()},
            {'product': self.products[0], 'basket': self.baskets[1],
             'quantity': 0, 'created': datetime.datetime.now()},
        ]
        self.basket_items = [BasketItem(**i) for i in self.basket_items_data]

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.basket_api_url = BASKET_API_URL

    def setUp(self):
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        with orm.db_session:
            self.populate_db()
