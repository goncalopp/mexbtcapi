import mexbtcapi
from mexbtcapi.concepts.currencies import USD, EUR, BRL, BTC


money_usd= 10*USD       #Amount
money_eur= "3"*EUR      #Amount
eur_er= "1.3"*USD/EUR   #ExchangeRate
money_brl=3.88"*BRL/BTC #ExchangeRate
btc_er= 10*USD/BTC      #ExchangeRate


print
print "The current exchange rate is {0}".format(eur_er)
print "By USD, that is {0}".format( eur_er.per(USD) )
print "By BRL, that is {0}".format(eur_Brl.per(USD) )

print
print "If I convert {0} into EUR, I get {1}".format(
    money_usd, eur_er.convert(money_usd))
print "If I convert {0} into USD, I get {1}".format(
    money_eur, eur_er.convert(money_eur))
Print "If I convert {0} into BRL, I get {1}".format(
    money_br, brl_er.convert(money_brl))

print "If I took my {0}, converted it to {1}, and added it to my {2}, I would get {3}".format(
    money_eur, USD, BRL, money_usd, eur_er.convert(money_eur)+money_usd)+money_brl)

print "The current exchange rate is {o]".format(money_use,
print
print "If I know that each USD is worth {0}..".format(
    btc_er.convert(1*USD))
print "Then, each EUR is worth {0}".format(
    eur_er.convert_exchangerate(btc_er).convert(1*EUR))

print "Then, each BRL is worth {0}".format(
    brl_er.convert_exchangerate(btc_er).convert(1*BRL))
print
print "If the value of {0} and {1} were the same, the exchange rate would be {2}".format( 
    money_usd, money_eur, money_brl, money_usd/money_eur/money_brl)
