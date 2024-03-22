import os
from response.requestHandler import RequestHandler

class StaticHandler(RequestHandler):
    def __init__(self, rootDir=''):
        super().__init__()
        self.filetypes = {
            ".js": "text/javascript",
            ".css": "text/css",
            ".jpg": "image/jpeg",
            ".png": "image/png",
            "notfound": "text/plain"
        }
        self.rootDir = rootDir
           
    def find(self, routeData): 
        file_path = self.rootDir + routeData
        split_path = os.path.splitext(routeData)
        extension = split_path[1]
        try:
            if extension in (".jpg", ".jpeg", ".png"):
                static_file = open(file_path, 'rb')
                self.contents = static_file.read()
            else:
                static_file = open(file_path, 'r')
                self.contents = static_file.read()
            self.setContentType(extension)
            self.setStatus(200)
            return True
        except:
            self.setContentType('notfound')
            self.setStatus(404)
            return False

    def setContentType(self, ext):
        self.contentType = self.filetypes[ext]
