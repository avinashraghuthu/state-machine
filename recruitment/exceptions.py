class InvalidWebUrl(Exception):

	def __init__(self, message, *args, **kwargs):
		Exception.__init__(self, message, *args, **kwargs)