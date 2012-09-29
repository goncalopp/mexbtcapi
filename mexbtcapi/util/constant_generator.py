def constant_generator(l, locals_dictionary):
    '''given a string list ( a list of names of constants), and the locals(),
    this function assigns each constant a number and registers them as variables'''
    values= range( len(l) )         #the constants' values - integers
    forward= dict( zip(l, values))  #name to number lookup
    reverse= l                      #number to name lookup
    locals_dictionary['list']= reverse
    locals_dictionary.update( forward ) #register variables
