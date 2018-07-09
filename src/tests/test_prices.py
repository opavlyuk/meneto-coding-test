from pony import orm

from src.tests import BaseCase
from src.entities import BasketItem


class TestBasketAPI(BaseCase):
    # TODO: add tests for other promotions
    @orm.db_session
    def test_without_promos(self):
        basket_id = self.baskets[1].id
        response = self.client.get(self.basket_api_url + str(basket_id))
        item_even = self.basket_items[5]
        total = item_even.product.price * item_even.quantity
        self.assertEqual(total, self.basket_items[5].total)
        self.assertEqual(total, BasketItem.get(id=response.get_json()['items'][1]).total)

    @orm.db_session
    def test_bofos_even(self):
        basket_id = self.baskets[0].id
        response = self.client.get(self.basket_api_url + str(basket_id))
        item_even = self.basket_items[1]
        subtotal = item_even.product.price * item_even.quantity
        total = subtotal - int(item_even.quantity / 2) * item_even.product.price
        self.assertEqual(total, self.basket_items[1].total)
        self.assertEqual(total, BasketItem.get(id=response.get_json()['items'][1]).total)

    @orm.db_session
    def test_bofos_odd(self):
        basket_id = self.baskets[0].id
        response = self.client.get(self.basket_api_url + str(basket_id))
        item_even = self.basket_items[0]
        subtotal = item_even.product.price * item_even.quantity
        total = subtotal - int(item_even.quantity / 2) * item_even.product.price
        self.assertEqual(total, self.basket_items[0].total)
        self.assertEqual(total, BasketItem.get(id=response.get_json()['items'][0]).total)
