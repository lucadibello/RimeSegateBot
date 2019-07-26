class Thumbnail:

    MODELS = []
    CATEGORIES = []
    URL = ""
    TITLE = ""
    VIDEO_URL = ""
    IMAGE_BYTES = ""

    def __init__(self, data, bytes=False):
        if not bytes:
            self.set_url(data)
        else:
            self.set_image_bytes(data)

    def set_image_bytes(self, bytes):
        self.IMAGE_BYTES = bytes

    def add_model(self, model: str):
        self.MODELS.append(model)

    def add_category(self, category: str):
        self.CATEGORIES.append(category)

    def set_models(self, models: list):
        self.MODELS = models

    def set_categories(self, categories: list):
        self.CATEGORIES = categories

    def set_url(self, url):
        self.URL = url

    def set_title(self, title):
        self.TITLE = title

    def set_video_url(self, video_url):
        self.VIDEO_URL = video_url

    def to_dict(self):
        return {
            "url": self.URL,
            "title": self.TITLE,
            "video_url": self.VIDEO_URL,
            "models": self.MODELS,
            "categories": self.CATEGORIES
        }
