def constant_generator(locals_dictionary, keys, values=None):
    '''given the locals(), a string list ( keys - a list of names of 
    constants), and their values, this function assigns each constant 
    it's value (or an integer, if values=None) and registers them as 
    variables'''
    if values==None:
        values= range( len(keys) )     #the constants' values - integers
    forward= dict( zip(keys, values))  #name to number lookup
    reverse= keys                      #number to name lookup
    locals_dictionary['list']= reverse
    locals_dictionary.update( forward ) #register variables
