class DownloadRequest:
    
    def __init__(self, url, filename):
        self.url = url
        self.filename = filename

    def get_dict(self):
        return {"url": self.url, "filename": self.filename }
