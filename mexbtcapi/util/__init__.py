'''Miscelaneous utilities functions'''
import logging
from collections import defaultdict

logging.getLogger(__name__)

def constant_generator(locals_dictionary, keys, values=None):
    """given the locals(), a string list ( keys - a list of names of
    constants), and their values, this function assigns each constant
    it's value (or an integer, if values=None) and registers them as
    variables"""
    if values is None:
        values = range(len(keys))       # the constants' values - integers
    forward = dict(zip(keys, values))   # name to number lookup
    reverse = keys                      # number to name lookup
    locals_dictionary['list'] = reverse
    locals_dictionary.update(forward)   # register variables

def group_by(iterable, key_func=lambda x: x, multi=False):
    '''Groups elements by the output of a given key function.
    The key function output can be either a iterable (multi=True) or a non-iterable (multi=False).
    If it's not a iterable, the returned groups are the key function output.
    If it's a iterable, the returned groups are the elements of that iterable.
    '''
    elements_by_group = defaultdict(set)
    for iter_el in iterable:
        k_out = key_func(iter_el)
        k_elems = k_out if multi else (k_out,)
        for k_elem in k_elems:
            elements_by_group[k_elem].add(iter_el)
    return elements_by_group
