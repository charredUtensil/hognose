#!/usr/bin/python3

from lib.lore.orders import ORDERS
from lib.lore.premises import PREMISES

ORDERS.dump_svg('lib/lore/orders.svg')
PREMISES.dump_svg('lib/lore/premises.svg')
