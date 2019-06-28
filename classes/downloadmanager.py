from classes.downloadrequest import DownloadRequest
import urllib.request
import urllib.parse
import datetime
import os
from progressbar import ProgressBar, Percentage, Bar

'''
This class is used for downloding content from the internet using the python native library 'urllib'.
'''
class DownloadManager:
    
    '''
        Constructor method. It saves into an attribute the requested resource.
    '''
    def __init__(self, download_req: DownloadRequest):
        self.download_req = download_req

        ''' Create progress bar '''
        self.pbar = None
        self.downloaded = 0

    '''
        This function is used for downloading the requested file 
        from the internet and save it into a specific folder.
    '''
    def download_file(self, save_path, overwriteCheck = False, automaticFilename = False):
        try:
            if not automaticFilename:
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
            if overwriteCheck:
                print("[!] Starting overwrite check")
                if not self.overwriteCheck(save_path, filename): return "[Overwrite] Error, with this filename you will overwrite a file"



            ''' Connects to the site and download the media '''
            urllib.request.urlretrieve(self.download_req.url, full_path, self.show_progress)

            print("[Downloader] File named {} saved correctly".format(full_path))
            
            return True

        except FileNotFoundError as f:
            ''' If the directory where is going to save the file doesn't exists '''
            print("[Downloader] Error while downloading file:", f)
            return "Error while saving file in {}".format(save_path)

    def overwriteCheck(self, path, file) -> bool:
        print("[Overwrite] Getting all the files in {} folder".format(path))
        onlyfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        ''' If there is a file with the same name '''
        if file in onlyfiles:
            print("[Overwrite] Found same filename, abort downloading process...")
            return False
        
        return True

    def show_progress(self, count, block_size, total_size):
        if self.pbar is None:
            self.pbar = ProgressBar(maxval=total_size)

        self.downloaded += block_size
        self.pbar.update(block_size)
        if self.downloaded == total_size:
            self.pbar.finish()
            pbar = None
            downloaded = 0

    @staticmethod
    def _get_file_extension(url: str) -> str:
        url = urllib.parse.urlparse(url).path
        return url[url.rfind("."):]

    @staticmethod
    def _normalize_filename(filename: str) -> str:
        return''.join(e for e in filename if e.isalnum())

