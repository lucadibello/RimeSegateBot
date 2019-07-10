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

    # Constructor method. It saves into an attribute the requested resource.
    def __init__(self, download_req: DownloadRequest, notifier: Notifier):
        self.download_req = download_req
        self.notifier = notifier

        ''' Create progress bar '''
        self.bar = None

    # This function is used for downloading the requested file
    # from the internet and save it into a specific folder.
    def download_file(self, save_path, overwrite_check=False, automatic_filename=False, new_download_method=True):
        try:
            full_path = ""
            if not new_download_method:

                self.notifier.notify("[Warning] You are using the old download method, this method does\
                             support only few sites. You rather switch to the new one by changhing the config file!")

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
            else:
                self.notifier.notify("[Info] Starting download")
                self._download(save_path, self.download_req.url)

            print("[Downloader] File named {} saved correctly".format(full_path))
            return True

        except FileNotFoundError as f:
            # If the directory where is going to save the file doesn't exists
            print("[Downloader] Error while downloading file:", f)
            return "Error while saving file in {}".format(save_path)

    TOT_DOWNLOADED = 0

    def _download(self, save_path, url):
        # 'format': 'bestvideo/bestaudio',

        ydl_opts = {
            'outtmpl': save_path + "/" + '%(title)s.%(ext)s',
            'progress_hooks': [self.download_hook],
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except youtube_dl.utils.DownloadError as err:
            print("Error detected: " + err.exc_info)

    def download_hook(self, d):
        if d["status"] == 'finished':
            print("Finished downloading video. Now converting...")
            self.notifier.notify("Converting video...")
        elif d["status"] == 'downloading':
            print("Downloading...")
        elif d['status'] == 'error':
            print("[Download Hook] Detected an error")
        else:
            print("[Download Hook] Unknown download status")

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
            self.notifier.notify("Current download percentage: " + percentage)

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
