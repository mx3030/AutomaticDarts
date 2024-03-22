class RequestHandler():
    def __init__(self):
        self.contentType = ""
        self.contents = ""

    def getContents(self):
        return self.contents 

    def setStatus(self, status):
        self.status = status

    def getStatus(self):
        return self.status

    def getContentType(self):
        return self.contentType 

    def getType(self):
        return 'static'
