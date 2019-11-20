class SYLFkException(Exception):
	def __init__(self, code='', message='Error'):
		self.code = code
		self.message = message

	def __str__(self):
		return self.message

class EndpointExistsError(SYLFkException):
	def __init__(self, message='Endpoint exists'):
		super().__init__(message)

class URLExistsError(SYLFkException):
	def __init__(self, message='URL exists'):
		super().__init__(message)