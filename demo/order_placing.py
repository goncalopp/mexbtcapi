import mexbtcapi
from mexbtcapi.concepts.currencies import USD, BTC

print "A order is the intention to exchange two amounts of currency"

print "If we want to exchange 10 dollars with 1 BTC, the order is "+str( 10*USD>>1*BTC )
print "If we want to exchange 10 dollars with at 3 USD/BTC, the order is "+str( 10*USD>>3*USD/BTC )
print "If we want to exchange 10 dollars at whatever price (market order), we get "+str( 10*USD>>None )
