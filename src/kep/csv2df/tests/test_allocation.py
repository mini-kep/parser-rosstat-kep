# b1 = Boundary('a', ['a', 'b', 'k', 'zzz'])
# assert b1.is_found is True  

# b2 = Boundary('hm!', ['a', 'b', 'k', 'zzz'])
# assert b2.is_found is False      

# p = Partition('a', 'k', ['a', 'b', 'k', 'zzz'])
# assert p.is_matched() is True
# assert 'Total of 4 rows' in str(p)

# r1 = get_boundaries ([dict(start='a', end='k'), dict(start='a', end='g1')],
                     # [['a'], ['b'], ['g12345'], ['zzz']])
# assert r1

# TEST: results in rrror
#get_boundaries ([dict(start='a', end='k'), dict(start='a', end='g1')],
#                     [['a'], ['b'], ['EEE'], ['zzz']])
