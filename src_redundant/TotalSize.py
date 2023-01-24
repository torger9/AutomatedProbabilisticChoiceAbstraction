from __future__ import print_function
from sys import getsizeof, stderr
from itertools import chain
from collections import deque
try:
    from reprlib import repr
except ImportError:
    pass

def total_size(o, handlers={}, verbose=False):
    """ Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter,
                   }
    all_handlers.update(handlers)     # user handlers take precedence
    seen = set()                      # track which object id's have already been seen
    default_size = getsizeof(0)       # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)
    
##for testing

# class animal:
    # def __init__(self, species, age):
        # animal.species = species
        # animal.age = age
    
    # def birthday(self):
        # print("This", self.species,"is turning",self.age,"today!")
        
# class pet(animal):
    # def __init__(self, age, species, name, owner):
        # super().__init__(age, species)
        # pet.name = name
        # pet.owner = owner
    
    # def introduction(self):
        # print("This is", self.name,"he is",self.owner,"'s",self.species,"and is",self.age,"years old")

# test_string1 = "abcdefg" 
# test_string2 = "abcdefghijklmnop"
# test_class1 = animal("bird", 26)
# test_class2 = pet("dog", 12, "Harley", "Aaron")
# test_dic1 = {1:"a", 2:"b", 3:"c", 4:"d", 5:"e", 6:"f", 7:"g"}
# test_dic2 = dict()

# for x in range(1,100):
    # test_dic2[x] = "qwertyuiopasdfghjklzxcvbnm"
    
# print(total_size(test_string1, verbose = False))
# print(getsizeof(test_string1))
# print(total_size(test_string2, verbose = False))
# print(getsizeof(test_string2))
# print(total_size(test_class1, verbose = False))
# print(getsizeof(test_class1))
# print(total_size(test_class2, verbose = False))
# print(getsizeof(test_class2))
# print(total_size(test_dic1, verbose = False))
# print(getsizeof(test_dic1))
# print(total_size(test_dic2, verbose = False))
# print(getsizeof(test_dic2))
