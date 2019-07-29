class Thumbnail:

    MODELS = []
    CATEGORIES = []
    URL = ""
    TITLE = ""
    VIDEO_URL = ""
    IMAGE_LOCAL_PATH = ""

    def __init__(self, data, local=False):
        if not local:
            self.set_url(data)
        else:
            self.set_image_local_path(data)

    def set_image_local_path(self, path):
        self.IMAGE_LOCAL_PATH = path

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
