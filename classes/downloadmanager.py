from classes.downloadrequest import DownloadRequest
from classes.notifier import Notifier
import urllib.request
import urllib.parse
import datetime
import youtube_dl
import os
from tqdm import tqdm

'''
This class is used for downloading content from the internet using the python native library 'urllib'.
'''


class DownloadManager:

    # Saves all the bytes downloaded bytes for the old download method hook
    TOT_DOWNLOADED = 0

    # Constructor method. It saves into an attribute the requested resource.
    def __init__(self, download_req: DownloadRequest, notifier: Notifier):
        self.download_req = download_req
        self.notifier = notifier

        ''' Create progress bar '''
        self.bar = None

    # This function is used for downloading the requested file
    # from the internet and save it into a specific folder.
    def download_file(self, save_path, overwrite_check=False, automatic_filename=False, new_download_method=True, convert_to_mp4 = False):
        try:
            full_path = ""
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
                # TODO: Move overwrite check before downloading
                if overwrite_check:
                    print("[!] Starting overwrite check")
                    if not self.overwrite_check(save_path, filename):
                        return "[Overwrite] Error, with this filename you will overwrite a file"

                # Connects to the site and download the media
                urllib.request.urlretrieve(self.download_req.url, full_path, self.download_progress)

            else:
                self.notifier.notify_information("Starting download")
                self.notifier.notify_information("\
                You are using the new download system witch supports a lot of websites,\
                <a href='https://ytdl-org.github.io/youtube-dl/supportedsites.html'>view the full list </a>.")

                self._download(save_path, self.download_req, automatic_filename, convert_to_mp4=convert_to_mp4)

            print("[Downloader] File named {} saved correctly".format(full_path))
            self.notifier.notify_success("File downloaded and saved correctly.")

            return True

        except Exception as f:
            # If the directory where is going to save the file doesn't exists
            print("[Downloader] Error while downloading file:", str(f))
            self.notifier.notify_error("Detected an error while downloading the resource: " + str(f))

    # New download method which supports over 1000+ websites using Youtube-DL embedded library
    def _download(self, save_path: str, download_request: DownloadRequest, automatic_filename: bool, convert_to_mp4=False):

        # Base downloader options
        ydl_opts = {
            'progress_hooks': [self.download_hook],
            'logger': DownloaderLogger(self.notifier),
        }

        if automatic_filename:
            ''' It will save the file with a unique filename based on the computer time (date and hour) '''
            filename = datetime.datetime.now().strftime("%m%d%Y-%H%M%S")

            """
                CONVERTER:
                
                    
                'format': "mp4",
            """

            # Add output format
            ydl_opts.update({'outtmpl': save_path + "/" + filename+".%(ext)s"})

        else:
            self.notifier.notify_warning("\
            You don't have 'automaticFilename' activated. If the resource you're downloading has the same name of\
             another already saved, it will overwrite the saved one. Use at your own risk!")

            # Add output format
            ydl_opts.update({'outtmpl': save_path + "/" + download_request.filename+".%(ext)s"})

        if convert_to_mp4:

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

        except youtube_dl.utils.DownloadError as err:
            print("[Youtube-DL] Error detected: " + err.exc_info)

    # Download hook for the new download method (Youtube-DL)
    def download_hook(self, d):
        if d["status"] == 'finished':
            print("Finished downloading video. Now converting...")
            self.notifier.notify_information("Converting video...")
            self._handle_download_finished(d['filename'])

        elif d["status"] == 'downloading':
            print(d['filename'], d['_percent_str'], d['_eta_str'])

        elif d['status'] == 'error':
            print("[Download Hook] Detected an error")
        else:
            print("[Download Hook] Unknown download status")

    # Download hook for the old download method
    def download_progress(self, block_size, total_size):

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

    def _handle_download_finished(self, file_path):
        self.notifier.send_video(file_path)

    @staticmethod
    def overwrite_check(path, file) -> bool:
        print("[Overwrite] Getting all the files in {} folder".format(path))
        only_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        # If there is a file with the same name
        if file in only_files:
            print("[Overwrite] Found same filename, abort downloading process...")
            return False

        return True

    @staticmethod
    def _get_file_extension(url: str) -> str:
        url = urllib.parse.urlparse(url).path
        return url[url.rfind("."):]

    @staticmethod
    def _normalize_filename(filename: str) -> str:
        return ''.join(e for e in filename if e.isalnum())


# This logger is used by Youtube-DL for logging all the information related to the download process
class DownloaderLogger(object):

    def __init__(self, notifier: Notifier):
        self.NOTIFIER = notifier

    def debug(self, msg):
        self.NOTIFIER.notify_debug(msg)

    def warning(self, msg):
        self.NOTIFIER.notify_warning(msg)

    def error(self, msg):
        self.NOTIFIER.notify_error(msg)