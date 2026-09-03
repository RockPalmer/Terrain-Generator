itera = 0

def prt(value):
	global itera

	print('  '*itera,end = '')
	print(value)
def up():
	global itera

	itera += 1
def dn():
	global itera

	itera -= 1