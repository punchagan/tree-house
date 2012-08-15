from datetime import datetime

def get_days_ago(date):
    delta = datetime.now() - date
    return delta.days

def product(sequence):
    return reduce(lambda x, y: x*y, sequence, 1)

def factorize(num):
    print num
    if num is None:
        return
    elif isinstance(num, basestring):
        num = int(num)
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    return [p for p in primes if num % p == 0]
