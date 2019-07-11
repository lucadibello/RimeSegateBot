from telegram import ParseMode


class Notifier:

    ERROR_EMOJI = "❌"
    WARNING_EMOJI = "⚠️"
    INFO_EMOJI = "ℹ️"
    SUCCESS_EMOJI = "✅"

    def __init__(self, update):
        self.update = update

    def _notify(self, message):
        self.update.message.reply_text(message, parse_mode=ParseMode.HTML)

    def notify_error(self, message):
        self._notify("{} {}".format(self.ERROR_EMOJI, message))

    def notify_warning(self, message):
        self._notify("{} {}".format(self.WARNING_EMOJI, message))

    def notify_information(self, message):
        self._notify("{} {}".format(self.INFO_EMOJI, message))

    def notify_success(self, message):
        self._notify("{} {}".format(self.SUCCESS_EMOJI, message))
