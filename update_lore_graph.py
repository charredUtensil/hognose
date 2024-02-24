#!/usr/bin/python3

from lib.lore.conclusions import SUCCESS, FAILURE
from lib.lore.events import (
    FOUND_HOARD, FOUND_HQ, FOUND_LOST_MINERS, FOUND_ALL_LOST_MINERS)
from lib.lore.orders import ORDERS
from lib.lore.premises import PREMISES

ORDERS.dump_svg('lib/lore/orders.svg')
PREMISES.dump_svg('lib/lore/premises.svg')

SUCCESS.dump_svg('lib/lore/success.svg')
FAILURE.dump_svg('lib/lore/failure.svg')

FOUND_HOARD.dump_svg('lib/lore/found_hoard.svg')
FOUND_HQ.dump_svg('lib/lore/found_hq.svg')
FOUND_LOST_MINERS.dump_svg('lib/lore/found_lost_miners.svg')
FOUND_ALL_LOST_MINERS.dump_svg('lib/lore/found_all_lost_miners.svg')
