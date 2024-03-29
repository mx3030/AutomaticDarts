import os
from response.requestHandler import RequestHandler
from routes.routes import htmlRoutes

class HTMLHandler(RequestHandler):
    def __init__(self, rootDir=''):
        super().__init__()
        self.contentType = 'text/html'
        self.rootDir = rootDir
        
    def find(self, routeData):
        try:
            html_path = os.path.join(self.rootDir, routeData)
            html_file = open(html_path, 'r')
            self.contents = html_file.read()
            self.setStatus(200)
            return True
        except:
            self.setStatus(404)
            return False

    def replace(self, marker, replacement):
        if marker in self.contents:
            self.contents = self.contents.replace(marker, replacement)
            return True
        else:
            return False
        


