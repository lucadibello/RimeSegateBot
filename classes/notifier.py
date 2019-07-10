
class Notifier:

    def __init__(self, update):
        self.update = update

    def notify(self, message):
        self.update.message.reply_text(message)
