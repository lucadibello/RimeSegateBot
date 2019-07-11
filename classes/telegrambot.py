

import logging
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)
from classes.downloadmanager import DownloadManager
from classes.downloadrequest import DownloadRequest
from classes.notifier import Notifier

'''
This telegram bot is able to download media (images and videos) from an url.
'''


class TelegramBot:

    # ConversationHandler steps
    SET_DOWNLOAD_URL, SET_FILE_NAME, START_DOWNLOAD = range(3)

    # Conversation texts
    DOWNLOAD_CONFIRMATION = "You want to start downloading this file? (y/n)"

    def __init__(self, config: dict):

        # Create an empty DownloadRequest object for the download ConversationHandler
        self.DOWNLOAD_REQUEST = DownloadRequest(None, None)

        # Saves the passed config into an attribute
        self.CONFIG = config

        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

        # Get logger object
        self.logger = logging.getLogger(__name__)

    def start_bot(self):
        # Create the bot object
        updater = Updater(self.CONFIG["token"], use_context=True)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # Register commands
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.help))

        # Add error handler
        dp.add_error_handler(self.error)

        # Conversation handler for the download request
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('download', self.download)],
            states={
                self.SET_DOWNLOAD_URL: [MessageHandler(Filters.text, self.check_download_url, pass_user_data=True)],
                self.SET_FILE_NAME: [MessageHandler(Filters.text, self.check_filename, pass_user_data=True)],
                self.START_DOWNLOAD: [MessageHandler(Filters.text, self.download_confirmation, pass_user_data=False)]
            },
            fallbacks=[MessageHandler(Filters.regex('exit'), self.cancel_download_wizard)]
        )

        # Register the conversation handler
        dp.add_handler(conversation_handler)

        # Start the bot
        updater.start_polling()

        print("[*] Bot started")

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

    '''
        COMMAND HANDLERS
    '''

    def start(self, update, context):
        # Send a message when the command /start is issued
        print("[Bot] Received start command from", self._get_user_id(update))
        update.message.reply_text("Hello my boi. Welcome.")

    @staticmethod
    def help(update, context):
        # Send to the user all the listed commands with their descriptions
        update.message.reply_text("Just type /download.")

    def download(self, update, context):
        print("[Bot] Received download command from", self._get_user_id(update))

        if self.CONFIG["noDownloadWizard"]:
            # For fast downloading change automatic filename to true
            self.CONFIG["automaticFilename"] = True
        else:
            # Start the download wizard
            update.message.reply_text("Oh hello! I'm here to guide you inside the downloading wizard!. "
                                      "PS: you can exit this wizard any time you want, you have just to type 'exit'")

        # Go to the first step
        update.message.reply_text("Send me an URL!")
        return self.SET_DOWNLOAD_URL

    def check_download_url(self, update, context):
        # Get last message sent by the user
        url = update.message.text

        # Check url
        if len(url) > 10:

            # Save url
            self.DOWNLOAD_REQUEST.url = url

            if self.CONFIG["noDownloadWizard"]:
                print("[NoWizard] Skip to downloading")
                # Download file
                self._download_file(self.DOWNLOAD_REQUEST, update)

                # TODO: Send the video to the user

                # End conversation
                return ConversationHandler.END
            else:
                # Check with regex if it's a link
                # TODO: URL CHECK
                update.message.reply_text("Ohh, look at that meme")

                # Check if automaticFilename is enabled or not in the config
                if not self.CONFIG["automaticFilename"]:

                    # Ask for the filename
                    update.message.reply_text("Second step: send me a filename")
                    return self.SET_FILE_NAME
                else:

                    # Go to the download confirmation
                    update.message.reply_text(self.DOWNLOAD_CONFIRMATION)
                    return self.START_DOWNLOAD
        else:
            # Ask again
            update.message.reply_text("Nope, you have to send me a right url, try again")
            return self.SET_DOWNLOAD_URL

    def check_filename(self, update, context):
        # Get last message sent by the user
        filename = update.message.text

        if 4 < len(filename) < 255:
            # TODO: CHECK FOR VALID FILENAME
            # Check with regex if it's a valid filename
            update.message.reply_text("Shitty name but is okay..")

            # Save filename
            self.DOWNLOAD_REQUEST.filename = filename

            # Pass to another step
            update.message.reply_text(self.DOWNLOAD_CONFIRMATION)
            return self.START_DOWNLOAD
        else:
            # Ask again
            return self.SET_FILE_NAME

    def download_confirmation(self, update, context):
        # Get last message sent by the user
        msg = update.message.text

        if msg == "y" or msg == "yes":
            update.message.reply_text("Starting downloading resource...")

            # Download file
            self._download_file(self.DOWNLOAD_REQUEST, update)

            # TODO: Send the video to the user

            # End conversation
            return ConversationHandler.END

        elif msg == "n" or msg == "no":
            # Abort download wizard
            update.message.reply_text("Download wizard aborted..")

            # Reset download request
            self.DOWNLOAD_REQUEST = DownloadRequest(None, None)

            # End conversation
            return ConversationHandler.END

        else:
            # Ask again for confirmation
            update.message.reply_text("Only y/yes or n/no allowed..")
            return self.START_DOWNLOAD

    def _download_file(self, request: DownloadRequest, session):
        manager = DownloadManager(request, notifier=Notifier(session))

        manager.download_file(
            self.CONFIG["saveFolder"],
            overwrite_check=self.CONFIG["overwriteCheck"],
            automatic_filename=self.CONFIG["automaticFilename"],
            new_download_method=self.CONFIG["newDownloadMethod"]
        )

    def cancel_download_wizard(self, update, context):
        # Exit the download wizard and reset the 'DOWNLOAD_REQUEST' attribute
        update.message.reply_text("Exited downloading wizard!")
        self.DOWNLOAD_REQUEST = DownloadRequest(None, None)

    def error(self, update, context):
        # Log Errors caused by Updates
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)

    @staticmethod
    def _get_user_id(update):
        return update.message.chat_id
