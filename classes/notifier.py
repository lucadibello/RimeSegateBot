from telegram import ParseMode


class Notifier:

    ERROR_EMOJI = "❌"
    WARNING_EMOJI = "⚠️"
    INFO_EMOJI = "ℹ️"
    SUCCESS_EMOJI = "✅"
    DEBUG_EMOJI = "🎌"

    def __init__(self, update, bot, send_video_timeout=80):
        self.update = update
        self.bot = bot
        self.VIDEO_TIMEOUT = send_video_timeout

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

    def notify_debug(self, message):
        self._notify("{} {}".format(self.DEBUG_EMOJI, message))

    def notify_custom(self, prefix, message):
        self._notify("{} {}".format(prefix, message))

    def send_video(self, video_path):
        self.notify_information("Uploading video to telegram...")
        self.bot.send_video(
            self.update.message.chat_id,
            open(video_path, 'rb'),
            timeout=self.VIDEO_TIMEOUT
        )
