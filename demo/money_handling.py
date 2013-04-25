import mexbtcapi
from mexbtcapi.concepts.currencies import USD, EUR, BTC


money_usd= 10*USD       #Amount
money_eur= "3"*EUR      #Amount
eur_er= "1.3"*USD/EUR   #ExchangeRate
btc_er= 10*USD/BTC      #ExchangeRate


print
print "The current exchange rate is {0}".format(eur_er)
print "By USD, that is {0}".format( eur_er.per(USD) )

print
print "If I convert {0} into EUR, I get {1}".format(
    money_usd, eur_er.convert(money_usd))
print "If I convert {0} into USD, I get {1}".format(
    money_eur, eur_er.convert(money_eur))

print 
print "If I took my {0}, converted it to {1}, and added it to my {2}, I would get {3}".format(
    money_eur, USD, money_usd, eur_er.convert(money_eur)+money_usd)

print
print "If I know that each USD is worth {0}..".format(
    btc_er.convert(1*USD))
print "Then, each EUR is worth {0}".format(
    eur_er.convert_exchangerate(btc_er).convert(1*EUR))


