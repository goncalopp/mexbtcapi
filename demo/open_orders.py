import mexbtcapi
from mexbtcapi.concepts.currencies import USD
from mexbtcapi import api

market= mexbtcapi.api.mtgox.market(USD)
me= market.getParticipant(API_KEY,API_SECRET)

open_orders= me.getOpenOrders()
print open_orders
