import os
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler
from response.staticHandler import StaticHandler
from response.htmlHandler import HTMLHandler
from response.badRequestHandler import BadRequestHandler
from routes.routes import htmlRoutes

def start_http(host, port, ws_port, client_dir, ssl_key, ssl_cert):
    httpd = CustomHTTPServer(host, port, Server, ws_port, client_dir)
    httpd.socket = ssl.wrap_socket(
        httpd.socket,
        keyfile=ssl_key,
        certfile=ssl_cert,
        server_side=True
    )
    print('starting http server on https://%s:%d' % (host, port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print('stopping http server on https://%s:%d' % (host, port))

class CustomHTTPServer(HTTPServer):
    def __init__(self, host, port, ServerClass, ws_port, client_dir, *args, **kwargs):
        super().__init__((host, port), ServerClass, *args, **kwargs)
        self.host = host
        self.port = port
        self.ws_port = ws_port
        self.client_dir = client_dir

class Server(BaseHTTPRequestHandler):   
    def do_HEAD(self):
        return

    def do_GET(self):
        split_path = os.path.splitext(self.path)
        request_extension = split_path[1]
        if request_extension == "" or request_extension == ".html":
            if self.path in htmlRoutes:
                handler = HTMLHandler(self.server.client_dir)
                handler.find(htmlRoutes[self.path]) 
                handler.replace('[config:host]', self.server.host)
                handler.replace('[config:ws_port]', str(self.server.ws_port))
            else:
                handler = BadRequestHandler() 
        else:
            handler = StaticHandler(self.server.client_dir)
            handler.find(self.path)
 
        self.respond(handler) 

    def do_POST(self):
        pass 

    def handle_http(self, handler):
        status_code = handler.getStatus()

        self.send_response(status_code)

        if status_code == 200:
            content = handler.getContents()
            self.send_header('Content-type', handler.getContentType())
        else:
            content = "404 Not Found"

        self.end_headers()

        if isinstance(content, bytes):
            return content
        else:
            return bytes(content, 'UTF-8')
            
    def respond(self, handler):
        response = self.handle_http(handler)
        self.wfile.write(response)
