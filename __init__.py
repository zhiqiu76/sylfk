from werkzeug.serving import run_simple
from sylfk.wsgi_adapter import wsgi_app
from werkzeug.wrappers import Response
import sylfk.exceptions as exceptions
from sylfk.helper import parse_static_key
from sylfk.route import Route
import os

ERROR_MAP = {
    '401': Response('<h1>401 Unknow or unsupported method</h1>', content_type='text/html; charset=UTF-8', status=401),
    '404': Response('<h1>404 Source Not Found</h1>', content_type='text/html; charset=UTF-8', status=404),
    '503': Response('<h1>503 Unknow function type</h1>', content_type='text/html; charset=UTF-8', status=503),
}
TYPE_MAP = {
    'css': 'text/css',
    'js': 'text/js',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
}

class ExecFunc(object):
    def __init__(self, func, func_type, **options):
        self.func = func
        self.func_type = func_type
        self.options = options


class SYLFk(object):
    """docstring for SYLFK"""
    def __init__(self, static_folder='static'):
        self.host = '127.0.0.1'
        self.port = 8086
        self.url_map = {}
        self.static_map = {}
        self.function_map = {}
        self.static_folder = static_folder
        self.route = Route(self)

    def dispatch_static(self, static_path):
        if os.path.exists(static_path):
            key = parse_static_key(static_path)
            doc_type = TYPE_MAP.get(key,'text/plain')
            with open(static_path, 'rb') as f:
                rep = f.read()
            return Response(rep, content_type=doc_type)
        else:
            return ERROR_MAP('404')
            
    def dispatch_request(self, request):
        url = '/' + '/'.join(request.url.split('/')[3:]).split('?')[0]
        if url.startswith('/' + self.static_folder + '/'):
            endpoint = 'static'
            url = url[1:]
        else:
            endpoint = self.url_map.get(url, None)
        headers = {'Server': 'SYL Web 0.1'}

        if endpoint is None:
            return ERROR_MAP['404']
        exec_function = self.function_map[endpoint]

        if exec_function.func_type == 'route':
            if request.method in exec_function.options.get('methods'):
                argcount = exec_function.func.__code__.co_argcount
                if argcount > 0:
                    rep = exec_function.func(request)
                else:
                    rep = exec_function.func()
            else:
                return ERROR_MAP['401']
        elif exec_function.func_type == 'view':
            rep = exec_function.func(request)
        elif exec_function.func_type == 'static':
            return exec_function.func(url)
        else:
            return ERROR_MAP['503']
        status = 200
        content_type = 'text/html'
        return Response(rep, content_type='%s; charset=UTF-8' % content_type, headers=headers, status=status)

    def run(self, host=None, port=None, **options):

        self.function_map['static'] = ExecFunc(func=self.dispatch_static, func_type='static')
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

    def bind_view(self, url, view_class, endpoint):
        self.add_url_rule(url, func=view_class.get_func(endpoint), func_type='view')

    def add_url_rule(self, url, func, func_type, endpoint=None, **options):
        if endpoint is None:
            endpoint = func.__name__

        if url in self.url_map:
            raise exceptions.URLExistsError

        if endpoint in self.function_map and func_type != 'static':
            raise exceptions.EndpointExistsError

        self.url_map[url] = endpoint

        self.function_map[endpoint] = ExecFunc(func, func_type, **options)

    def load_controller(self, controller):
        name = controller.__name__()
        for rule in controller.url_map:
            self.bind_view(rule['url'], rule['view'], name + '.' + rule['endpoint'])