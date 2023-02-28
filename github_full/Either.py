#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 12:41:26 2017

@author: amcp011
"""

class Either(object):
    pass

class Left(Either):
    def __init__(self, v): self.v = v
    def is_left(self): return True
    def is_right(self): return False
    def value(self): return self.v 

class Right(Either):
    def __init__(self, v): self.v = v
    def is_left(self): return False
    def is_right(self): return True
    def value(self): return self.v 


class Maybe(object):
    pass

class Nothing(Maybe):
    def is_nothing(self): return True
    def is_just(self): return False
    def value(self): raise Exception('Called value() on Nothing value')

class Just(Maybe):
    def __init__(self, v): self.v = v
    def is_nothing(self): return False
    def is_just(self): return True
    def value(self): return self.v