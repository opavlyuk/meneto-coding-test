item_promos = []
global_promos = []


def item_promo(promo_func):
    item_promos.append(promo_func)
    return promo_func


def global_promo(promo_func):
    global_promos.append(promo_func)
    return promo_func


@item_promo
def buy_one_get_one_free(item):
    item.item_total -= int(item.quantity / 2) * item.product.price


@global_promo
def discount_10_percent(cart):
    if cart.basket_total > 20:
        cart.basket_total -= cart.basket_total / 10


@global_promo
def discount_loyalty(cart):
    if cart.customer.has_loyalty:
        cart.basket_total -= cart.basket_total / 100 * 2
