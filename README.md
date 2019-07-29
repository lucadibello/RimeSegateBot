# RimeSegate's Telegram Bot
This telegram bot is able to download videos from over 800 websites thanks to [Youtube-dl]("https://github.com/ytdl-org/youtube-dl"). All the downloaded videos are uploaded autonomously to [OpenLoad.co]("https://openload.co/").
After the upload process it will generate a video preview using 9 frames of the downloaded video with [OpenCV]("https://opencv.org/").

## Features

- 2 download methods (urlretrieve + youtube-dl)
- 2 preview generation methods (OpenLoad + OpenCV)
- Config file
- Multi-Platform (UNIX + Windows)
- Video converter (to MP4)
- and much more!

## Setup
```shell
pip3 install -r requirements.txt 
```

## Config file

### File example

```json
{
  "automaticFilename": false,
  "saveFolder": "download",
  "overwriteCheck": false,
  "noDownloadWizard": true,
  "newDownloadMethod": true,
  "videoToMP4": false,
  "videoTimeout": 9999,
  "readTimeout": 400,
  "connectTimeout": 400,
  "thumbnailArgumentDivider": ";",
  "openloadThumbnail": false,
  "openloadThumbnailDelaySeconds": 60,
  "token": "<BOT_TOKEN>",
  "openload_api_login": "<OPENLOAD_API_LOGIN>",
  "openload_api_key": "<OPENLOAD_API_KEY>"
}
```
