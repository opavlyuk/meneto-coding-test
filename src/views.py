import datetime
from http import HTTPStatus

from flask import json, request
from flask.views import MethodView
from pony import orm

from src.settings import BASKET_API_URL
from src.entities import Basket, Customer, Product, BasketItem


class BasketAPI(MethodView):
    """RESTful API view for Baskets.

    /baskets/       GET	    Gives a list of all baskets
    /baskets/       POST    Creates a new basket
    /baskets/<id>	GET     Shows a single basket
    /baskets/<id>	PUT     Updates a single basket
    /baskets/<id>	DELETE  Deletes a single basket
    """
    @orm.db_session
    def get_all(self):
        """Get JSON response with all baskets.

        Returns:
            JSON response with all baskets.
        """
        baskets = orm.select(b for b in Basket)
        response = json.jsonify([i.to_dict() for i in baskets])
        return response

    @orm.db_session
    def get_single(self, basket_id):
        """Get JSON response single basket by id.

        Returns:
            JSON response with basket with given id.
        """
        basket = Basket.get(id=basket_id)
        if basket:
            return json.jsonify(basket.to_dict())
        return '', HTTPStatus.NOT_FOUND

    # TODO: refactor and move to items API, when ready.
    @staticmethod
    def create_items(basket, items):
        """Create new basket items.

        Raises:
            KeyError: If new items contains non-existent products.
        """
        basket_items = []
        if items is None:
            return
        for p_id in items:
            product = Product.get(id=p_id['id'])
            if product is None:
                raise KeyError('Product with id {} not found'.format(p_id['id']))
            new_item = BasketItem(
                product=product,
                quantity=p_id['quantity'],
                created=datetime.datetime.now(),
            )
            basket_items.append(new_item)
        basket.items = basket_items


    @orm.db_session
    def create_basket(self):
        """Create basket and return JSON response with it.

        Returns:
            201 CREATED JSON response with new basket and `Location` header,
            pointing to new basket url.
        """
        req = request.get_json()
        new_basket = Basket(created=datetime.datetime.now(),
                            customer=Customer.get(id=req['customer_id']),
                            items=[])
        try:
            self.create_items(new_basket, req.get('items', []))
        except KeyError:
            # Clean-up new basket if exception occurred during item adding
            new_basket.delete()
            raise
        resp = json.jsonify(new_basket.to_dict())
        resp.status_code = HTTPStatus.CREATED
        resp.headers['Location'] = BASKET_API_URL + str(new_basket.id)
        return resp

    @orm.db_session
    def delete_basket(self, basket_id):
        """Delete basket by id.

        Args:
            basket_id (int): id for basket to delete.
        Returns:
            204 response if basket with given id exists, else 404 response.
        """
        basket = Basket.get(id=basket_id)
        if basket is None:
            return '', HTTPStatus.NOT_FOUND
        basket.delete()
        return '', HTTPStatus.NO_CONTENT

    @orm.db_session
    def update_basket(self, basket_id):
        """Update basket by id.

        Args:
            basket_id (int): id for basket to update.
        Returns:
            200 response with updated basket if object exists, else 404 response
        Raises:
            KeyError: If updated basket items contains non-existent products.
        """
        basket = Basket.get(id=basket_id)
        if basket is None:
            return '', HTTPStatus.NOT_FOUND
        req = request.get_json()

        items_to_update = req.get('items')
        self.create_items(basket, items_to_update)
        basket.set(customer=req['customer_id'])
        return json.jsonify(basket.to_dict())

    def get(self, basket_id):
        if basket_id is None:
            response = self.get_all()
        else:
            response = self.get_single(basket_id)
        return response

    def post(self):
        response = self.create_basket()
        return response

    def put(self, basket_id):
        response = self.update_basket(basket_id)
        return response

    def delete(self, basket_id):
        response = self.delete_basket(basket_id)
        return response
