import ast

def csv_to_list(csv):
	list = []
	try:
		list = csv.split(',')
		for l in range(0, len(list)):
			list[l] = list[l].strip()
	except:
		pass
	return list

def list_to_csv(list):
	csv = ''
	try:
		csv = list[0]
		for l in range(1,len(list)):
			csv += ", " + list[l]
	except:
		pass
	return csv

def string_to_object(s):
	try:
		o = ast.literal_eval(s)
	except:
		o = None
	return o
