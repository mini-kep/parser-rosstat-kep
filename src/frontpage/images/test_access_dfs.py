# -*- coding: utf-8 -*-

# test for access_dfs.py
# 

from urllib import request
import access_dfs as a_d


def do_test():

	print('\nValidating compose_url(): ', end='')
	try:
		assert a_d.compose_url('x') == (""
			"https://raw.githubusercontent.com/"
			"epogrebnyak/mini-kep/master/data/processed/latest/dfx.csv")
		print('OK')
	except AssertionError:
		print('FAILED!')
		return

	print('Trying to load dataframe: ', end='')
	try:
		response = request.urlopen(a_d.compose_url('a'))
		assert response.code == 200
		print('OK')
	except AssertionError:
		print('FAILED! (response code != 200)')
		return
	except Exception:
		print('FAILED! (unknown error)')
		return

	dfs = None
	print('Executing get_dfs_from_web(): ', end='')
	try:
		dfs = a_d.get_dfs_from_web()
		print('OK')
	except Exception:
		print('FAILED! (failed to load)')
		return

	try:
		assert dfs['a'].shape == (18, 31)
		assert dfs['q'].shape == (74, 38)
		assert dfs['m'].shape == (223, 36)
	except AssertionError:
		print('WARNING: Dataframes size changed',
				'or they are parsed incorrectly')


do_test()
print()