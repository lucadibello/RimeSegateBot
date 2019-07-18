from telegram import ParseMode


class Notifier:
    ERROR_EMOJI = "❌"
    WARNING_EMOJI = "⚠️"
    INFO_EMOJI = "ℹ️"
    SUCCESS_EMOJI = "✅"
    DEBUG_EMOJI = "🎌"

    ''' OpenLoad Prefix Emoji'''
    OPENLOAD_FILE_NAME = "📁"
    OPENLOAD_FILE_SIZE = "🏋️"
    OPENLOAD_FILE_TYPE = "🗃️"
    OPENLOAD_URL = "🌎"

    def __init__(self, update, bot, send_video_timeout=80):
        self.update = update
        self.bot = bot
        self.VIDEO_TIMEOUT = send_video_timeout

    def _notify(self, message, silent=False):
        self.update.message.reply_text(message, parse_mode=ParseMode.HTML, disable_notification=silent)

    def notify_error(self, message):
        self._notify("{} {}".format(self.ERROR_EMOJI, message))

    def notify_warning(self, message):
        self._notify("{} {}".format(self.WARNING_EMOJI, message))

    def notify_information(self, message):
        self._notify("{} {}".format(self.INFO_EMOJI, message))

    def notify_success(self, message):
        self._notify("{} {}".format(self.SUCCESS_EMOJI, message))

    def notify_debug(self, message):
        self._notify("{} {}".format(self.DEBUG_EMOJI, message), silent=True)

    def notify_custom(self, prefix, message):
        self._notify("{} {}".format(prefix, message))

    def send_video(self, video_path):
        self.notify_information("Uploading video to telegram...")
        self.bot.send_video(
            self.update.message.chat_id,
            open(video_path, 'rb'),
            timeout=self.VIDEO_TIMEOUT
        )

    def notify_openload_response(self, response):
        response_beautified = "{} Name: {}\n\r" \
                              "{} Size: {} Bytes\n\r" \
                              "{} Media type: {}\n\r" \
                              "{} Url: {}\n\r".format(self.OPENLOAD_FILE_NAME, response["name"],
                                                      self.OPENLOAD_FILE_SIZE, response["size"],
                                                      self.OPENLOAD_FILE_TYPE, response["content_type"],
                                                      self.OPENLOAD_URL, response["url"])

        self._notify(response_beautified)

    def send_photo_bytes(self, image_bytes, caption=""):
        if not caption:
            self.bot.send_photo(
                self.update.message.chat_id,
                image_bytes,
            )
        else:
            self.bot.send_photo(
                self.update.message.chat_id,
                image_bytes,
                caption=caption
            )
