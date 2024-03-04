from random import choice

words = 'avocado biscuit chocolate doughnut eclaire fudge goulash haddock icing juice koala lemon melon nut'.split(' ')

def random_slug():
    return '-'.join(choice(words) for i in range(3))
