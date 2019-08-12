from verystreamwrapper import VeryStreamWrapper

def main():
    uploader = VeryStreamWrapper("a368582c85e54eff8998", "bstQddvFtfD")
    print("Uploading large file...")
    a = uploader.upload_large_file("download/M_rain_ZZ.mp4")
    print(a)
    print("File uploaded correctly")

if __name__ == '__main__':
    main()