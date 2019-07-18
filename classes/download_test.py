from downloadrequest import DownloadRequest
from downloadmanager import DownloadManager
from tqdm import tqdm

def main():
    request = DownloadRequest("http://mirrors.standaloneinstaller.com/video-sample/page18-movie-4.mts", "test")
    manager = DownloadManager(request)
    manager.download_file("../download")

if __name__ == '__main__':
    main()