from werkzeug.wrappers import Request

def wsgi_app(app, environ, start_response):

	request = Request(environ)

	response = app.dispatch_request(request)

	return response(environ, start_response)