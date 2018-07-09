from datetime import datetime

from pony import orm

from src.promos import item_promos, global_promos
from src.settings import DB_CONF

# TODO: move to __init__.py
db = orm.Database()
db.bind(provider=DB_CONF['provider'], filename=DB_CONF['filename'])


class Basket(db.Entity):
    _table_ = 'baskets'
    customer = orm.Required('Customer')
    created = orm.Required(datetime)
    items = orm.Set('BasketItem')

    @property
    def total(self):
        """Get total price for all items in basket with applied promos."""
        self.basket_total = sum(i.total for i in self.items)
        [promo(self) for promo in global_promos]
        return round(self.basket_total, 2)

    def to_dict(self, with_collections=True):
        """Return entity dict representation.

        Add property support for entity dict representation.
        """
        d = super().to_dict(with_collections=with_collections)
        d['total'] = self.total
        return d


class BasketItem(db.Entity):
    _table_ = 'basketItems'
    product = orm.Required('Product')
    quantity = orm.Required(int)
    created = orm.Required(datetime)
    basket = orm.Optional(Basket)

    @property
    def total(self):
        self.item_total = self.product.price * self.quantity
        [promo(self) for promo in item_promos]
        return round(self.item_total, 2)


class Product(db.Entity):
    _table_ = 'products'
    title = orm.Required(str)
    price = orm.Required(float)
    created = orm.Required(datetime)
    basket_items = orm.Set(BasketItem)


class Customer(db.Entity):
    _table_ = 'customers'
    name = orm.Required(str, unique=True)
    baskets = orm.Set(Basket)
    has_loyalty = orm.Optional(bool, default=False)
    created = orm.Required(datetime)


db.generate_mapping(create_tables=True)
