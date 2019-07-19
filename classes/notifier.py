from _ast import Dict

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
        """
        Parametrized constructor method.

        :param update: Telegram.ext.Update object which identifies the user.
        :param bot: Telegram.ext.Bot object which identifies the bot used to send messages/files.
        :param send_video_timeout: (Optional, Default=80) Timeout in seconds used for sending the videos to the user.
        """

        self.update = update
        self.bot = bot
        self.VIDEO_TIMEOUT = send_video_timeout

    def _notify(self, message, silent=False):
        """
        This private method is the base for all the message notifiers, it send a message to a specific
        user using the bot attribute. The send

        :param message: Message to send to the user.
        :param silent: (Optional, Default=False) If it's True the user will ear a notification sound when the
        message is receives, otherwise the notification will be send in "silent mode" (no notification sound)
        """

        self.update.message.reply_text(message, parse_mode=ParseMode.HTML, disable_notification=silent)

    def notify_error(self, message):
        """
        Notify an exception/error to the user.
        :param message: Exception/error message to send to the user.
        """
        self._notify("{} {}".format(self.ERROR_EMOJI, message))

    def notify_warning(self, message):
        """
        Notify a warning to the user.
        :param message: Warning message to send to the user.
        """

        self._notify("{} {}".format(self.WARNING_EMOJI, message))

    def notify_information(self, message):
        """
        Notify an information to the user.
        :param message: Information message to send to the user.
        """

        self._notify("{} {}".format(self.INFO_EMOJI, message))

    def notify_success(self, message):
        """
        Notify a success information to the user.
        :param message: Success message to send to the user.
        """

        self._notify("{} {}".format(self.SUCCESS_EMOJI, message))

    def notify_debug(self, message):
        """
        Notify a debug information to the user.
        :param message: Debug message to send to the user.
        """

        self._notify("{} {}".format(self.DEBUG_EMOJI, message), silent=True)

    def notify_custom(self, prefix, message):
        """
        Notify the user with a message with a custom prefix.
        :param prefix: Prefix to use in the message.
        :param message: Message to send to the user.
        """

        self._notify("{} {}".format(prefix, message))

    def send_video(self, video_path):
        """
        This method is used to send a video to the user. WARNING: A bot can send a max of 50MB!
        :param video_path: Path of the video to send.
        :return:
        """

        self.notify_information("Uploading video to telegram...")
        self.bot.send_video(
            self.update.message.chat_id,
            open(video_path, 'rb'),
            timeout=self.VIDEO_TIMEOUT
        )

    def notify_openload_response(self, response: Dict):
        """
        This method is used to notify the user that the video has been successfully uploaded to OpenLoad.co
        :param response: OpenLoad.co response after upload as Dict object (Dictionary).
        """

        response_beautified = "{} Name: {}\n\r" \
                              "{} Size: {} Bytes\n\r" \
                              "{} Media type: {}\n\r" \
                              "{} Url: {}\n\r".format(self.OPENLOAD_FILE_NAME, response["name"],
                                                      self.OPENLOAD_FILE_SIZE, response["size"],
                                                      self.OPENLOAD_FILE_TYPE, response["content_type"],
                                                      self.OPENLOAD_URL, response["url"])

        self._notify(response_beautified)

    def send_photo_bytes(self, image_bytes, caption=False):
        """
        This method is used to send an image using a byte array.

        :param image_bytes: Image as byte array.
        :param caption: (Optional, Default=False) If a caption is set i will send the image
        and a caption in the same message.
        """

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
