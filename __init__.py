from werkzeug.serving import run_simple
from sylfk.wsgi_adapter import wsgi_app
from werkzeug.wrappers import Response

class SYLFk(object):
    """docstring for SYLFK"""
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 8086

    def dispatch_request(self, request):
        status = 200
        headers = {
            'Server':'Shiyanlou Framework',
        }
        return Response('<h1>Hello, Framework<h1>', content_type='text/html', headers=headers, status=status)

    def run(self, host=None, port=None, **options):
        for key, value in options.items():
            if value is not None:
                self.__setattr__(key, value)
        if host:
            self.host = host
        if port:
            self.port = port

        run_simple(hostname=self.host, port=self.port, application=self, **options)

    def __call__(self, environ, start_response):
        return wsgi_app(self, environ, start_response)
