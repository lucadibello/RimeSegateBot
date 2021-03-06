import datetime
import os
import urllib.parse
import urllib.request
from io import BytesIO

import kthread
import requests
import youtube_dl
from openload.api_exceptions import *
from tqdm import tqdm

from classes.downloadrequest import DownloadRequest
from classes.notifier import Notifier
from classes.openloadwrapper import OpenloadWrapper
from classes.previewgenerator import PreviewGenerator
from classes.telegrambot import TelegramBot


class DownloadManager:
    """
    This class is used for downloading content from the internet using the python
    native library 'urllib' or "Youtube-DL". After the download the video will be
    uploaded autonomously to OpenLoad (<a hred="http://openload.co">Visit website</a>).
    """

    # Saves all the bytes downloaded bytes for the old download method hook
    TOT_DOWNLOADED = 0

    # True when the download has finished
    DOWNLOAD_FINISHED = False

    # Set all uploaders to "None"
    OL = None
    VS = None

    # Constructor method. It saves into an attribute the requested resource.
    def __init__(self, download_req: DownloadRequest, notifier: Notifier, uploader, online_thumbnail=False):
        """
        Parametrized constructor method.

        :param download_req: DownloadRequest object that describes the user request (video url and filename).
        :param notifier: Notifer object that will be used to notify the user (send messages)
        :param uploader: OpenloadWrapper or VeryStreamWrapper object that will be used to upload
        the video on Openload.co or VeryStream.com website
        """

        self.download_req = download_req
        self.notifier = notifier
        self.online_thumbnail = online_thumbnail

        if isinstance(uploader, OpenloadWrapper):
            print("[DownloadManager] Detected OpenLoad uploader")
            self.OL = uploader
        else:
            print("[DownloadManager] Detected VeryStream uploader")
            self.VS = uploader

        ''' Create progress bar (used with the old download method) '''
        self.bar = None

    def download_file(self, save_path, overwrite_check=False, automatic_filename=False, new_download_method=True,
                      convert_to_mp4=False):

        """
        This function is used for downloading the requested file from the internet and save it into a specific folder.

        :param save_path: Folder where the file will be saved

        :param overwrite_check: (Optional, default=False) If it's true the program will check if there's already a
        file with the same name in the "save_path" folder otherwise it will do any type of check.

        :param automatic_filename: (Optional, default=False) If it's true the program will generate a unique
        filename to the downloaded video (current datetime in yyyMMdd-hhmmss format) otherwise the video will
        have the one chosen before saved in the DownloadRequest object attribute.

        :param new_download_method: (Optional, default=True) If it's true the program will use the new download
        method (Youtube-DL embedded) which supports +800 websites and multiple videos
        streams (es: segmented videos, normal videos, ...) otherwise it will use the plain HTTP Get request
        do try to download the video from the web page (WARNING: it supports only the normal videos)

        :param convert_to_mp4: (Optional, default=False) If it's true the program will convert all the downloaded
        videos to mp4 format, otherwise the video file will not be converted after the download.
        This option is supported only using the new download method and it requires ffmpeg installed on the system.
        (WARNING: This video conversion can comport bad video quality and/or video/audio dystrosions)

        :return: True if the download process finished successful otherwise a string object containing the error message.
        """

        try:
            if not new_download_method:
                self.notifier.notify_warning(
                    "You are using the old download method, this method does\
                    support only few sites and less options.\
                    You rather switch to the new one by changing the config file!"
                )

                if convert_to_mp4:
                    self.notifier.notify_warning("The file conversion is supported only using the new download method.")

                if not automatic_filename:
                    ''' Create the urllib object for downloading files on the internet '''
                    filename = self.download_req.filename

                else:
                    ''' It will save the file with a unique filename based on the computer time (date and hour) '''
                    current_time = datetime.datetime.now()
                    filename = current_time.strftime("%m%d%Y-%H%M%S")

                ''' Normalize the name (only numbers and letters) '''
                filename = self._normalize_filename(filename) + self._get_file_extension(self.download_req.url)

                ''' Build path '''
                full_path = os.path.join(save_path, filename)

                ''' Check for overwrite if it's enabled '''
                if overwrite_check:
                    print("[!] Starting overwrite check")
                    if not self.overwrite_check(save_path, filename):
                        return "[Overwrite] Error, with this filename you will overwrite a file"

                # Connects to the site and download the media
                urllib.request.urlretrieve(self.download_req.url, full_path, self.download_progress)

                # Uploads the video on OpenLoad
                self._handle_download_finished(full_path, self.TOT_DOWNLOADED)

                self.DOWNLOAD_FINISHED = True

                print("[Downloader] File named {} saved correctly".format(full_path))
                self.notifier.notify_success("File downloaded and uploaded correctly!.")

            else:
                self.notifier.notify_information("Starting download")
                self.notifier.notify_information("\
                You are using the new download system witch supports a lot of websites,\
                <a href='https://ytdl-org.github.io/youtube-dl/supportedsites.html'>view the full list </a>.")

                print("[DownloadManager] Starting download in another thread")

                download_process = kthread.KThread(
                    target=self._download,
                    args=(save_path, self.download_req, automatic_filename, convert_to_mp4,)
                )

                # download_process.daemon = True
                download_process.start()

                print("[DownloadManager] Download started in another thread: {}".format(download_process))

                # Add process to the list of processes
                TelegramBot.DOWNLOAD_PROCESSES[TelegramBot.get_user_id(self.notifier.get_session())] = download_process

                # self._download(save_path, self.download_req, automatic_filename, convert_to_mp4=convert_to_mp4)

            # self.wait_download_to_finish()
            return True

        except FileNotFoundException as f:
            # If the directory where is going to save the file doesn't exists
            print("[Downloader] Error of type {} while downloading file:".format(type(f).__name__), str(f))
            self.notifier.notify_error("Detected an error while downloading the resource: " + str(f))

    def _download(self, save_path: str, download_request: DownloadRequest, automatic_filename: bool,
                  convert_to_mp4=False):
        """
        This method allows the user to download a video using the new download method (Youtube-DL embedded).

        :param save_path: Path where the video will be saved.

        :param download_request: DownloadRequest object that describes the user request (video url and filename).

        :param automatic_filename: If it's true the program will generate a unique
        filename to the downloaded video (current datetime in yyyMMdd-hhmmss format) otherwise the video will
        have the one chosen before saved in the DownloadRequest object attribute.

        :param convert_to_mp4: (Optional, default=False) If it's true the program will convert all the downloaded
        videos to mp4 format, otherwise the video file will not be converted after the download.
        This option is supported only using the new download method and it requires ffmpeg installed on the system.
        (WARNING: This video conversion can comport bad video quality and/or video/audio dystrosions)
        """

        # Base downloader options
        ydl_opts = {
            'progress_hooks': [self.download_hook],
            'logger': DownloaderLogger(self.notifier),
        }

        if automatic_filename:
            ''' It will save the file with a unique filename based on the computer time (date and hour) '''
            filename = datetime.datetime.now().strftime("%m%d%Y-%H%M%S")

            # Add output format
            full_path = os.path.join(save_path, filename)
            ydl_opts.update({'outtmpl': full_path + ".%(ext)s"})

        else:
            self.notifier.notify_warning("\
            You don't have 'automaticFilename' activated. If the resource you're downloading has the same name of\
             another already saved, it will overwrite the saved one. Use at your own risk!")

            # Add output format
            full_path = os.path.join(save_path, download_request.filename)
            ydl_opts.update({'outtmpl': full_path + ".%(ext)s"})

        if convert_to_mp4:
            self.notifier.notify_error(
                "MP4 conversion has a bug. It will upload on OpenLoad and then will convert the video...\
                Please check the Youtube-DL's Download Hook"
            )

            ydl_opts.update({'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]})

        # Start download
        print("[Youtube-DL] generated config:")
        print(ydl_opts)

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([download_request.url])

                self.DOWNLOAD_FINISHED = True
                print("[Downloader] File named {} saved correctly".format(full_path))
                self.notifier.notify_success("File downloaded correctly with Youtube-DL!.")

        except youtube_dl.utils.DownloadError as err:
            print("[Youtube-DL] Error detected: " + err.exc_info)

        # Remove index from download process
        del TelegramBot.DOWNLOAD_PROCESSES[TelegramBot.get_user_id(self.notifier.get_session())]

    def download_hook(self, d):
        """
        Download hook for the new download method (Youtube-DL)

        :param d: All the file information (filename, full size, ...).
        """

        if d["status"] == 'finished':
            print("Finished downloading video. Now converting...")
            self.notifier.notify_information("Converting video...")
            self._handle_download_finished(d['filename'], d["total_bytes"])

        elif d["status"] == 'downloading':
            print(d['filename'], d['_percent_str'], d['_eta_str'])

        elif d['status'] == 'error':
            print("[Download Hook] Detected an error")
        else:
            print("[Download Hook] Unknown download status")

    def download_progress(self, block_size, total_size):
        """
        Download hook for the old download method. It shows a progress bar using "tqdm" library.

        :param block_size: Downloaded bytes.
        :param total_size: Total size of the file.
        """

        if self.bar is None:
            self.bar = tqdm(total=total_size, unit="b", unit_scale=True, dynamic_ncols=True)

        # Update progress bar
        self.bar.update(block_size)
        self.bar.refresh()

        # Notify user

        # Get current total
        self.TOT_DOWNLOADED += block_size
        temp = self.TOT_DOWNLOADED / total_size
        percentage = temp * 100

        if percentage % 10 == 0:
            # Notify user every 10% step
            self.notifier.notify_information("Current download percentage: " + percentage)

    def _handle_download_finished(self, file_path: str, file_size: float):
        """
        This method handles all the post-download process, so upload on OpenLoad the downloaded video
        and download the video thumbnail generated by OpenLoad.

        :param file_path: File downloaded, used for uploading the video on OpenLoad.co
        :param file_size: File size in bytes, used for estimate the video thumbnail generation by OpenLoad.co
        """

        try:
            response = ""
            if self.VS is not None:
                # If is set the VeryStream uploader, it will upload the video on VeryStream.com
                self.notifier.notify_information(
                    "Uploading file to VeryStream.com, this will take some time "
                    "(depends from file size and internet upload speed)"
                )

                # response = self.VS.upload_file(file_path)
                response = self.VS.upload_large_file(file_path)
                print("[DownloadManager] Video uploaded on VeryStream.com and returned a response")
                print(response)

            elif self.OL is not None:
                # Otherwise, if is set the OpenLoad uploader, it will upload the video on OpenLoad.co

                self.notifier.notify_information(
                    "Uploading file to OpenLoad.com, this will take some time "
                    "(depends from file size and internet upload speed)"
                )

                # Upload file to Openload
                response = self.OL.upload_file(file_path)
                print("[DownloadManager] Video uploaded on OpenLoad.co and returned a response")
                print(response)

            self.notifier.notify_uploader_response(response)

            from classes.thumbnail import Thumbnail

            if self.online_thumbnail:
                thumb_url = ""
                if self.VS is not None:
                    # Get thumbnail from VeryStrean
                    self.notifier.notify_information("Wating VeryStream to generate a thumbnail...")

                    thumb_url = self.VS.get_thumbnail_when_ready(response.get("id"), delay=60)

                    # Checker
                    while thumb_url is None:
                        print("[DownloadManager] Invalid thumbnail (None), retry to get a thumbnail")
                        thumb_url = self.OL.get_thumbnail_when_ready(response.get("id"), delay=5)

                    print("[DownloadManager] Got a thumbnail url from VeryStream.com:", thumb_url)

                else:
                    # Get thumbnail from OpenLoad
                    self.notifier.notify_information("Wating OpenLoad to generate a thumbnail...")

                    def get_thumbnail_estimated_generation_size(size: float):

                        if size is None:
                            return None
                        else:
                            # Latest test: 4% every ~20.28s (File size: 424.46 MB) -> 4.2445 MB/s == 4450680.832 Byte/s
                            BYTES_ANALYSED_EVERY_20_SEC = 4450681
                            time = (size / BYTES_ANALYSED_EVERY_20_SEC) * 20
                            return time

                    estimated_time = get_thumbnail_estimated_generation_size(file_size)

                    if estimated_time is None:
                        self.notifier.notify_warning("Can't estimate a thumbnail generation time...")
                    else:
                        self.notifier.notify_warning(
                            "Estimated time for thumbnail generation {} seconds".format(estimated_time))

                    # thumb_url = self.OL.get_thumbnail_when_ready(response.get("id"), delay=estimated_time)
                    thumb_url = self.OL.get_thumbnail_when_ready(response.get("id"), delay=60)

                    # Checker
                    while thumb_url is None:
                        print("[DownloadManager] Invalid thumbnail (None), retry to get a thumbnail")
                        thumb_url = self.OL.get_thumbnail_when_ready(response.get("id"), delay=5)

                    print("[DownloadManager] Got a thumbnail url from OpenLoad.co:", thumb_url)

                TelegramBot.THUMBNAILS[TelegramBot.get_user_id(self.notifier.get_session())] = Thumbnail(thumb_url)

                self.notifier.notify_success(
                    "I found the thumbnail, to generate a caption use '/thumbnail' command. "
                    "This will start a wizard, just follow the steps!"
                )

            else:

                # Generate thumbnail using downloaded video
                print("[DownloadManager] Generating thumbnail using video: {}".format(file_path))
                generator = PreviewGenerator()
                import cv2

                try:
                    response = generator.generate_preview(file_path, "thumbnails")

                    if not response:
                        self.notifier.notify_error("Error while generating thumbnail...")
                    else:
                        print("File path", response['path'])

                        TelegramBot.THUMBNAILS[TelegramBot.get_user_id(self.notifier.get_session())] = Thumbnail(
                            response["path"],
                            local=True
                        )

                        self.notifier.notify_success(
                            "I've generated a preview in {} seconds. to generate a caption use '/thumbnail' "
                            "command.This will start a wizard, just follow the steps!".format(response["seconds"])
                        )
                except cv2.error as ex:
                    print("[DownloadManager] Can't generate a preview.. Error message:", str(ex))
                    self.notifier.notify_error(
                        "OpenCV cannot generate a proper thumbnail with this video... Ask the developer"
                    )

            # Delete file after download
            os.remove(file_path)

        except PermissionDeniedException as pde:
            self.notifier.notify_error("Permission denied detected while trying to upload data to openload:" + str(pde))
            print("[DownloadManager] Permission denied detected while uploading video to openload: " + str(pde))

    @staticmethod
    def download_image_stream(url: str) -> BytesIO:
        """
        This method allows the user to download a file into the RAM (get an array of bytes)
        :param url: Resource to download
        :return: BytesIO object that contains all the downloaded data
        """

        r = requests.get(url)
        return BytesIO(r.content)

    @staticmethod
    def overwrite_check(path, file) -> bool:
        """
        This method checks if there is a file with same name in the passed path.
        :param path: Directory where will do the check
        :param file: Filename to check
        :return: True if there isn't a file with the same name, otherwise False
        """

        print("[Overwrite] Getting all the files in {} folder".format(path))
        only_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        # If there is a file with the same name
        if file in only_files:
            print("[Overwrite] Found same filename, abort downloading process...")
            return False

        return True

    @staticmethod
    def _get_file_extension(url: str) -> str:
        """
        This method is used to get the file extension out of a url (example: http://example.com/video.mp4)
        :param url: Url where the extension will be extracted
        :return: File extension as string object.
        """

        url = urllib.parse.urlparse(url).path
        return url[url.rfind("."):]

    @staticmethod
    def _normalize_filename(filename: str) -> str:
        """
        This method is used to "clean" a filename, in fact it removes all the characters that are
        not a number or a letter (alphanumeric).
        :param filename: Filename to clean.
        :return: Cleaned filename.
        """

        return ''.join(e for e in filename if e.isalnum())


class DownloaderLogger(object):
    """
    This logger is used by Youtube-DL for logging all the information related to the download process
    """

    def __init__(self, notifier: Notifier):
        """
        Parametrized constructor method.
        :param notifier: Notifier object that will be used to send to the user messages.
        """

        self.NOTIFIER = notifier

    def debug(self, msg):
        """
        This method will notify the user the debug information
        :param msg: Debug message that will be send to the user.
        """
        self.NOTIFIER.notify_debug(msg)

    def warning(self, msg):
        """
        This method will notify the user the warnings generated during the download process
        :param msg: Warning message that will be send to the user.
        """
        self.NOTIFIER.notify_warning(msg)

    def error(self, msg):
        """
        This method will notify the user the errors generated during the download process
        :param msg: Error message that will be send to the user.
        """
        self.NOTIFIER.notify_error(msg)
