import ast
from kivy.uix.image import Image

from kivy.graphics import Rectangle

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

def set_button_icon(b, icon):
	b.canvas.after.clear()
	with b.canvas.after:
		Rectangle(pos=((b.pos[0] + b.size[0] / 2) - (b.size[1] / 2), b.pos[1]),
				  size=(b.size[1], b.size[1]), source=icon)


class Singleton(type):
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


def IconButton(Image):
	pass
