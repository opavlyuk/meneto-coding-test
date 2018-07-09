from http import HTTPStatus

from pony import orm

from src.entities import Basket, BasketItem
from src.tests import BaseCase


class TestBasketAPI(BaseCase):
    @orm.db_session
    def test_get_all(self):
        response = self.client.get(self.basket_api_url)
        self.assertEqual(HTTPStatus.OK, response.status_code, 'Status code.')
        self.assertTrue(response.is_json)
        self.assertEqual(len(self.basket_data), len(response.get_json()))

    @orm.db_session
    def test_get_single_valid(self):
        basket_id = self.baskets[1].id
        response = self.client.get(self.basket_api_url + str(basket_id))
        self.assertEqual(HTTPStatus.OK, response.status_code, 'Status code.')
        self.assertTrue(response.is_json)
        expected_obj = Basket.get(id=basket_id).to_dict()
        del (expected_obj['created'])
        # Used deprecated assertion as temporary solution
        self.assertDictContainsSubset(expected_obj, response.get_json())

    @orm.db_session
    def test_get_single_not_exists(self):
        basket_id = 5
        response = self.client.get(self.basket_api_url + str(basket_id))
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code, 'Status code.')

    @orm.db_session
    def test_post_valid(self):
        new_basket = {'customer_id': 1,
                      'items': [{'id': 1, 'quantity': 2},
                                {'id': 2, 'quantity': 10}]}
        response = self.client.post(self.basket_api_url, json=new_basket)
        self.assertEqual(HTTPStatus.CREATED, response.status_code, 'Status code.')
        self.assertIn('Location', response.headers)
        self.assertTrue(response.headers['Location'].endswith(self.basket_api_url + '3'))
        self.assertTrue(response.is_json)
        actual_obj_in_db = Basket.get(id=len(self.baskets) + 1)
        expected_obj = {'customer': new_basket['customer_id'], 'id': 3, 'items': [8,9]}
        self.assertIsNotNone(actual_obj_in_db, 'Object is in DB.')
        # Used deprecated assertion as temporary solution
        self.assertDictContainsSubset(expected_obj,
                                      actual_obj_in_db.to_dict(with_collections=True))
        self.assertDictContainsSubset(expected_obj, response.get_json())
        self.assertEqual(len(self.basket_items) + 2,
                         len(orm.select(i for i in BasketItem)[:]))

    @orm.db_session
    def test_post_non_existent_customer(self):
        new_basket = {'customer_id': self.customers[-1].id + 1,
                      'items': [{'id': 1, 'quantity': 2},
                                {'id': 2, 'quantity': 10}]}
        response = self.client.post(self.basket_api_url, json=new_basket)
        self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, response.status_code)
        actual_obj_in_db = Basket.get(id=len(self.baskets) + 1)
        self.assertIsNone(actual_obj_in_db)
        self.assertEqual(len(self.basket_items), len(orm.select(i for i in BasketItem)[:]))

    @orm.db_session
    def test_post_without_items(self):
        new_basket = {'customer_id': self.customers[0].id}
        response = self.client.post(self.basket_api_url, json=new_basket)
        self.assertEqual(HTTPStatus.CREATED, response.status_code)
        self.assertIn('Location', response.headers)
        self.assertTrue(response.headers['Location'].endswith(self.basket_api_url + '3'))
        self.assertTrue(response.is_json)
        actual_obj_in_db = Basket.get(id=len(self.baskets) + 1)
        expected_obj = {'customer': new_basket['customer_id'],
                        'id': len(self.baskets) + 1, 'items': []}
        self.assertIsNotNone(actual_obj_in_db, 'Object is in DB.')
        # Used deprecated assertion as temporary solution
        self.assertDictContainsSubset(expected_obj,
                                      actual_obj_in_db.to_dict(with_collections=True))
        self.assertDictContainsSubset(expected_obj, response.get_json())
        self.assertEqual(len(self.basket_items),
                         len(orm.select(i for i in BasketItem)[:]))

    @orm.db_session
    def test_post_with_bad_items(self):
        new_basket = {'customer_id': self.customers[0].id,
                      'items': [{'id': self.products[-1].id + 1, 'quantity': 2},
                                {'id': self.products[-1].id + 2, 'quantity': 10}]}
        response = self.client.post(self.basket_api_url, json=new_basket)
        self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, response.status_code)
        actual_obj_in_db = Basket.get(id=len(self.baskets) + 1)
        self.assertIsNone(actual_obj_in_db)
        self.assertEqual(len(self.basket_items), len(orm.select(i for i in BasketItem)[:]))

    @orm.db_session
    def test_put_valid(self):
        basket_id_to_update = self.baskets[0].id
        updated_basket = {'customer_id': self.customers[1].id,
                          'items': [{'id': self.products[1].id, 'quantity': 12},
                                    {'id': self.products[0].id, 'quantity': 9}]}
        response = self.client.put(self.basket_api_url + str(basket_id_to_update),
                                   json=updated_basket)
        self.assertEqual(HTTPStatus.OK, response.status_code, 'Status code.')
        self.assertTrue(response.is_json)
        actual_obj_in_db = Basket.get(id=basket_id_to_update)
        expected_obj = actual_obj_in_db.to_dict()
        del (expected_obj['created'])
        # Used deprecated assertion as temporary solution
        resp_body = response.get_json()
        self.assertDictContainsSubset(expected_obj, resp_body)
        self.assertEqual(2, len(list(actual_obj_in_db.items)))
        import time; time.sleep(0.7)
        for n, i in enumerate(actual_obj_in_db.items):
            self.assertEqual(updated_basket['items'][n]['id'], i.product.id,
                             'Updated item product id for item {}'.format(i))
            self.assertEqual(updated_basket['items'][n]['quantity'], i.quantity,
                             'Updated item quantity for item {}'.format(i))

    @orm.db_session
    def test_put_non_existent(self):
        basket_id_to_update = self.baskets[-1].id + 1
        updated_basket = {'customer_id': self.customers[1].id,
                          'items': [{'id': self.products[1].id, 'quantity': 12},
                                    {'id': self.products[0].id, 'quantity': 9}]}
        response = self.client.put(self.basket_api_url + str(basket_id_to_update),
                                   json=updated_basket)
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code, 'Status code.')
        self.assertEqual(len(self.basket_data), len(orm.select(b for b in Basket)[:]))

    @orm.db_session
    def test_put_without_items(self):
        basket_id_to_update = self.baskets[0].id
        updated_basket = {'customer_id': self.customers[-1].id}
        response = self.client.put(self.basket_api_url + str(basket_id_to_update),
                                   json=updated_basket)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertTrue(response.is_json)
        actual_obj_in_db = Basket.get(id=basket_id_to_update)
        expected_obj = {'customer': updated_basket['customer_id'],
                        'id': basket_id_to_update, 'items': [1, 2, 3, 4]}
        # Used deprecated assertion as temporary solution
        self.assertDictContainsSubset(expected_obj,
                                      actual_obj_in_db.to_dict(with_collections=True))
        self.assertDictContainsSubset(expected_obj, response.get_json())

    @orm.db_session
    def test_put_items_empty(self):
        basket_id_to_update = self.baskets[0].id
        updated_basket = {'customer_id': self.customers[-1].id, 'items': []}
        response = self.client.put(self.basket_api_url + str(basket_id_to_update),
                                   json=updated_basket)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertTrue(response.is_json)
        actual_obj_in_db = Basket.get(id=basket_id_to_update)
        expected_obj = {'customer': updated_basket['customer_id'],
                        'id': basket_id_to_update, 'items': []}
        # Used deprecated assertion as temporary solution
        self.assertDictContainsSubset(expected_obj,
                                      actual_obj_in_db.to_dict(with_collections=True))
        self.assertDictContainsSubset(expected_obj, response.get_json())

    @orm.db_session
    def test_delete_valid(self):
        basket_id_to_del = self.baskets[0].id
        response = self.client.delete(self.basket_api_url + str(basket_id_to_del))
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
        self.assertIsNone(Basket.get(id=basket_id_to_del))

    @orm.db_session
    def test_delete_non_existent(self):
        basket_id_to_del = self.baskets[-1].id + 1
        response = self.client.delete(self.basket_api_url + str(basket_id_to_del))
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        self.assertEqual(len(self.basket_data), len(self.baskets))

