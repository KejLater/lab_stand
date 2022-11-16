def RNG():
    from random import random, randint
    return format(randint(-100, 100) + random(), '.2f')

