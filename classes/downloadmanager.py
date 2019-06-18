from classes.downloadrequest import DownloadRequest
import urllib.request
import os

'''
This class is used for downloding content from the internet using the python native library 'urllib'.
'''
class DownloadManager:
    
    '''
        Constructor method. It saves into an attribute the requested resource.
    '''
    def __init__(self, download_req: DownloadRequest):
        self.download_req = download_req

    '''
        This function is used for downloading the requested file 
        from the internet and save it into a specific folder.
    '''
    def download_file(self, save_path, overwriteCheck = False, automaticFilename = False):
        try:
            if not automaticFilename:
                ''' Create the urllib object for downloading files on the internet '''
                full_path = os.path.join(save_path,self.download_req.filename + self._get_file_extension(self.download_req.url))
            else:
                ''' It will save the file with the same name of the downloaded one '''
                full_path = os.path.join(save_path,os.path.basename(self.download_req.url))

            if overwriteCheck:
                print("WIP")

            ''' Connects to the site and download the media '''
            urllib.request.urlretrieve(self.download_req.url, full_path)

            print("File named {} saved correctly".format(full_path))

            return True

        except FileNotFoundError as f:
            ''' If the directory 'downloads' doesn't exists '''
            return "Error while saving file in {}".format(save_path)

    @staticmethod
    def _get_file_extension(url: str) -> str:
        return url[url.rfind("."):]