import logging
import os
import sys
from functools import wraps
from threading import Thread

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

from classes.downloadrequest import DownloadRequest
from classes.notifier import Notifier
from classes.openloadwrapper import OpenloadWrapper
from classes.urlchecker import UrlChecker
from classes.thumbnail import Thumbnail

LIST_OF_ADMINS = ["238454100", "68736753"]


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if str(user_id) not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            context.bot.send_message(chat_id=update.effective_message.chat_id,
                                     text="Permission denied, you have to be an admin to use this command")
            return
        return func(update, context, *args, **kwargs)

    return wrapped


class TelegramBot:
    """ This telegram bot is able to download media (images and videos) from an url. """

    # ConversationHandler steps
    SET_DOWNLOAD_URL, SET_FILE_NAME, START_DOWNLOAD = range(3)

    # Thumbnail conversation steps
    SET_VIDEO_NAME, SET_MODEL, SET_CATEGORIES, SET_URL = range(4)

    # Conversation texts
    DOWNLOAD_CONFIRMATION = "You want to start downloading this file? (y/n)"

    THUMBNAILS = {68736753: Thumbnail("https://thumb.oloadcdn.net/splash/pZSrxv2Pxgk/vo1AjwKzRmo.jpg")}

    def __init__(self, config: dict):
        """
        Parametrized constructor method.

        :param config: Config dictionary loaded using config.py and config.json
        """

        # Create an empty DownloadRequest object for the download ConversationHandler
        self.DOWNLOAD_REQUEST = DownloadRequest(None, None)

        # Saves the passed config into an attribute
        self.CONFIG = config

        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

        # Get logger object
        self.logger = logging.getLogger(__name__)

        # Create bot object
        self.BOT = None

        # Create openload object
        self.OL = OpenloadWrapper(self.CONFIG["openload_api_login"], self.CONFIG["openload_api_key"])

    def start_bot(self):
        """ This method is used to start the telegram bot. """

        # Create the bot object
        updater = Updater(self.CONFIG["token"], use_context=True, request_kwargs={
            'read_timeout': self.CONFIG["readTimeout"],
            'connect_timeout': self.CONFIG["connectTimeout"]
        })

        self.BOT = updater.bot

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        def stop_and_restart():
            """ Gracefully stop the Updater and replace the current process with a new one """
            updater.stop()
            print("[!] Stopped updater")

            print("[!] Replacing this process with a new one...")

            # Replaces the old process with a new one
            os.execl(sys.executable, sys.executable, *sys.argv)

        @restricted
        def restart(update, context):
            """
            This method handles the '/restart' command and use the '@restricted' wrapper to check if the user
            is in the admin list (LIST_OF_ADMINS string array)
            """
            print("[!] Restarting bot...")
            update.message.reply_text('Bot is restarting...')

            # Start restart operation in different thread
            Thread(target=stop_and_restart).start()

        # Register commands
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.help))
        dp.add_handler(CommandHandler("restart", restart))
        dp.add_handler(CommandHandler("thumbnail_b1", self.thumbnail_b1))

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
            fallbacks=[MessageHandler(Filters.regex('^exit$'), self.cancel_download_wizard)]
        )

        thumbnail_conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('thumbnail', self.thumbnail)],
            states={
                 self.SET_VIDEO_NAME: [MessageHandler(Filters.text, self.thumbnail_set_video_name, pass_user_data=True)],
                 self.SET_MODEL: [MessageHandler(Filters.text, self.thumbnail_set_model, pass_user_data=True)],
                 self.SET_CATEGORIES: [MessageHandler(Filters.text, self.thumbnail_set_categories, pass_user_data=True)],
                 self.SET_URL: [MessageHandler(Filters.text, self.thumbnail_set_url, pass_user_data=True)]
             },
            fallbacks=[MessageHandler(Filters.regex('^exit$'), self.cancel_download_wizard)]
        )

        # Register all the the conversation handler
        dp.add_handler(conversation_handler)
        dp.add_handler(thumbnail_conversation_handler)

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
        """
        This method handles the '/start'
        """

        # Send a message when the command /start is issued
        print("[Bot] Received start command from", self.get_user_id(update))

        update.message.reply_text("Hello my boi. Welcome.")

    @restricted
    @staticmethod
    def help(update, context):
        """
        This method handles the '/help' command
        """

        # Send to the user all the listed commands with their descriptions
        update.message.reply_text("Just type /download.")

    @restricted
    def download(self, update, context):
        """
        This method handles the '/download' command. It start a conversation (3 steps)
        with the user to determine the URL of the video resource to download and
        the filename (if set in the config file)
        """

        print("[Bot] Received download command from", self.get_user_id(update))

        # Create unique notifier for this user (every update -> different notifier)
        notifier = Notifier(update, self.BOT)

        if self.CONFIG["noDownloadWizard"]:
            # For fast downloading change automatic filename to true
            self.CONFIG["automaticFilename"] = True

        else:
            # Start the download wizard
            notifier.notify_information("Oh hello! I'm here to guide you inside the downloading wizard!.\
                                      PS: you can exit this wizard any time you want, you have just to type 'exit'")

        # Go to the first step
        notifier.notify_custom("1️", "Send me a video url")

        return self.SET_DOWNLOAD_URL

    def check_download_url(self, update, context):
        """
        This method represents the 1° step of the download conversation. It asks the user to insert the video URL. It will check if the URL is formatted well (validator-like) and if
        the site is reachable (HTTP GET Request with Reponse Code 200)
        """

        # Create unique notifier for this user (every update -> different notifier)
        notifier = Notifier(update, self.BOT)

        # Get last message sent by the user
        url = update.message.text

        # Check url
        if UrlChecker.full_check(url):

            # Save url
            self.DOWNLOAD_REQUEST.url = url

            if self.CONFIG["noDownloadWizard"]:
                print("[NoWizard] Skip to downloading")
                # Download file
                self._download_file(self.DOWNLOAD_REQUEST, update)

                # End conversation
                return ConversationHandler.END
            else:
                notifier.notify_success("The url is well-formatted and the website is reachable.")

                # Check if automaticFilename is enabled or not in the config
                if not self.CONFIG["automaticFilename"]:

                    # Ask for the filename
                    notifier.notify_custom("2️⃣", "Send me a filename")

                    return self.SET_FILE_NAME
                else:

                    # Go to the download confirmation
                    update.message.reply_text(self.DOWNLOAD_CONFIRMATION)
                    return self.START_DOWNLOAD
        else:
            # Ask again
            notifier.notify_error("The url is not valid or the website is not reachable.")
            return self.SET_DOWNLOAD_URL

    def check_filename(self, update, context):
        """
        This method represents the 2° step of the download conversation. It asks the user to insert a
        valid filename for the video (the filename have to be from 5 to 254 characters of length).
        This step can be skipped if the config file the "automaticFilename" flag is set True or if
        the "noDownloadWizard" flag is set at True.
        """

        # Get last message sent by the user
        filename = update.message.text

        if 4 < len(filename) < 255:
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
        """
        This method represents the 3° and last step of the download conversation. It asks the user to
        approve or deny the download process.
        This is done by requesting a user input: If the user responds "y" or "yes" the download process continues,
        if the user responds "n" or "no" the download process stops and will reset all the related variables.
        Otherwise, if the user send a non valid input, it will ask again to send a new answer.
        """

        # Get last message sent by the user
        msg = update.message.text

        if msg == "y" or msg == "yes":
            update.message.reply_text("Starting downloading resource...")

            # Download file
            self._download_file(self.DOWNLOAD_REQUEST, update)

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
        """
        This method uses the DownloadManager class to download the user request.

        :param request: DownloadRequest object that describes the user download request (url and filename"
        :param session: Current user session. (Telegram.ext.Update object)
        """
        from classes.downloadmanager import DownloadManager

        manager = DownloadManager(
            request,
            notifier=Notifier(session, self.BOT, self.CONFIG["videoTimeout"]),
            openload=self.OL
        )

        manager.download_file(
            self.CONFIG["saveFolder"],
            overwrite_check=self.CONFIG["overwriteCheck"],
            automatic_filename=self.CONFIG["automaticFilename"],
            new_download_method=self.CONFIG["newDownloadMethod"],
            convert_to_mp4=self.CONFIG["videoToMP4"]
        )

    @restricted
    def thumbnail(self, update, context):
        notifier = Notifier(update, self.BOT)

        try:
            print("[Thumbnail] Check if user with id {} has downloaded any videos..".format(self.get_user_id(update)))
            thumbnail = self.THUMBNAILS.get(self.get_user_id(update))

            if thumbnail is None:
                print("You have first to upload the video to OpenLoad to access this function..")
                notifier.notify_warning("You have to download and upload a video on OpenLoad to use this function properly.")
                return ConversationHandler.END

            else:
                notifier.notify_success(
                    "We detected that you have already uploaded a video on OpenLoad so you can start build your caption"
                )

                notifier.notify_success(
                    "This is a wizard that helps you to generate a nice caption for your thumbnail. "
                    "You can type 'exit' in any moment to abort the process!"
                )

                print("[Thumbnail] User {} has a valid thumbnail URL saved: {}".format(
                    self.get_user_id(update),
                    thumbnail.URL)
                )

                notifier.notify_information("Select a video name. PS: It can't be only spaces!")

                return self.SET_VIDEO_NAME

        except KeyError:
            print("[Thumbnail] Can't find user id in list..")
            print(self.THUMBNAILS)
            notifier.notify_warning("You haven't downloaded any videos...")

            return ConversationHandler.END

    def thumbnail_set_video_name(self, update, context):
        notifier = Notifier(update, self.BOT)

        # Get last message sent by the user
        msg = update.message.text.strip()

        print("[Thumbnail] User {} select a message: {}".format(
            self.get_user_id(update),
            msg
        ))

        if len(msg) > 0:
            self.THUMBNAILS[self.get_user_id(update)].set_title(msg)
            notifier.notify_success("'{}' is a valid video name".format(msg))

            notifier.notify_information(
                "Please, list all the models present in the video (names separated with '{}' ).\
                (Example: Sasha Grey;Mia Khalifa;...".format(self.CONFIG["thumbnailArgumentDivider"])
            )

            return self.SET_MODEL
        else:
            # Invalid name detected
            notifier.notify_error("Invalid name, please try again")
            return self.SET_VIDEO_NAME

        # Get models and set them into the Thumbnail object

    def thumbnail_set_model(self, update, context):
        notifier = Notifier(update, self.BOT)

        # Get last message sent by the user
        msg = update.message.text.strip()

        # Get models and set them into the Thumbnail object
        models = msg.split(self.CONFIG["thumbnailArgumentDivider"])
        self.THUMBNAILS[self.get_user_id(update)].set_models(models)
        notifier.notify_success('I detected {} models!'.format(len(models)))

        print("[Thumbnail] User {} selected {} model(s): {}".format(
            self.get_user_id(update),
            len(models),
            models
        ))

        # Proceed to the next step
        notifier.notify_information(
            'Now tell me all the categories of the video (categories separated by {})'.format(
                self.CONFIG["thumbnailArgumentDivider"]
            )
        )

        return self.SET_CATEGORIES

    def thumbnail_set_categories(self, update, context):
        notifier = Notifier(update, self.BOT)

        # Get last message sent by the user
        msg = update.message.text.strip()

        # Get categories and set them into the Thumbnail object
        categories = msg.split(self.CONFIG["thumbnailArgumentDivider"])
        self.THUMBNAILS[self.get_user_id(update)].set_categories(categories)
        notifier.notify_success('I detected {} categories!'.format(len(categories)))

        print("[Thumbnail] User {} selected {} categories: {}".format(
            self.get_user_id(update),
            len(categories),
            categories
        ))

        # Proceed to the next step
        notifier.notify_information(
            'Now tell me the url of the video!'.format(
                self.CONFIG["thumbnailArgumentDivider"]
            )
        )

        return self.SET_URL

    def thumbnail_set_url(self, update, context):
        notifier = Notifier(update, self.BOT)
        checker = UrlChecker()

        # Get last message sent by the user
        url = update.message.text.strip()

        if checker.full_check(url):
            # Url valid (well-formatted & reachable)
            notifier.notify_success("The URL is well-formatted and reachable via HTTP GET requests.")
            self.THUMBNAILS[self.get_user_id(update)].set_video_url(url)

            print("[Thumbnail] User {} selected a url for the caption: {}".format(
                self.get_user_id(update),
                url
            ))

            # Send image with caption
            notifier.notify_information("Generating image with caption...")
            self._build_thumbnail_message(notifier, self.THUMBNAILS[self.get_user_id(update)])

            notifier.notify_success(
                "Message generated successfully. "
                "If you don't like it you can type '/thumbnail' again."
            )

            # End conversation
            return ConversationHandler.END
        else:
            # Error detected by checker, retry again with another URL
            notifier.notify_error(
                "The url is not well-formatted or is not reachable via HTTP GET requests... Check the URL and try again"
            )

            # Restart to 'set URL'
            return self.SET_URL

    @staticmethod
    def _build_thumbnail_message(notifier: Notifier, thumbnail: Thumbnail):
        from classes.downloadmanager import DownloadManager

        print("[Thumbnail] Generating message with these values:")
        print(thumbnail.to_dict())

        notifier.send_photo_bytes(
            DownloadManager.download_image_stream(thumbnail.URL),
            caption=notifier.generate_caption(thumbnail)
        )

    @restricted
    def thumbnail_b1(self, update, context):
        notifier = Notifier(update, self.BOT)
        try:
            print("[Thumbnail] Check if user with id {} has downloaded any videos..".format(self.get_user_id(update)))
            thumbnail_url = self.THUMBNAILS.get(self.get_user_id(update)).URL

            if thumbnail_url is None:
                print("You have first to upload the video to OpenLoad to access this function..")
            else:
                from classes.downloadmanager import DownloadManager
                print("You have a thumbnail!!! " + thumbnail_url)
                notifier.send_photo_bytes(
                    DownloadManager.download_image_stream(thumbnail_url)
                )
        except KeyError:
            print("[Thumbnail] Can't find user id in list..")
            print(self.THUMBNAILS)
            notifier.notify_warning("You haven't downloaded any videos...")

    def cancel_download_wizard(self, update, context):
        """
        This method is called when the conversation abort command is detected.
        It quits the conversation between the user and the bot and resets the DownloadRequest object.
        """

        # Exit the download wizard and reset the 'DOWNLOAD_REQUEST' attribute
        update.message.reply_text("Exited downloading wizard!")
        self.DOWNLOAD_REQUEST = DownloadRequest(None, None)

    def cancel_thumbnail_wizard(self, update, context):
        notify = Notifier(update, self.BOT)
        url = self.THUMBNAILS[self.get_user_id(update)].URL
        self.THUMBNAILS[self.get_user_id(update)] = Thumbnail(url)

        notify.notify_information("Exited thumbnail wizard, I've cleared all saved data! "
                                  "If you wanna build again a message you can use '/thumbnail' without any problem")

        return ConversationHandler.END

    def error(self, update, context):
        """
        This method is called when the bot telegram detects an exception/issue
        that does not allow the correct operation of one or more functions.
        """

        # Log Errors caused by Updates
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)

    @staticmethod
    def get_user_id(update):
        """
        Wrapper function that simplify the work of getting the user_id out of a Telegram.ext.Update object (session)
        :param update: Telegram.ext.Update object (session object)
        :return: The user id
        """

        return update.message.chat_id
