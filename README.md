# RimeSegate's Telegram Bot

## Settings file

### File example

```json
{
    "automaticFilename": false,
    "saveFolder": "download",
    "overwriteCheck": true,
    "noDownloadWizard": true,
    "token": "862902894:AAGaL24Ny56emXeUkXuPuVsMXAdtSburcAr"
}
```

## Openload setup

### Create environment variables

#### Bash
Open your bash terminal and use this script:
```bash
export OPENLOAD_LOGIN=<YOUR API LOGIN>
export OPENLOAD_KEY=<YOUR API KEY>
```

#### Windows
Open powershell and use this script:

```powershell
[Environment]::SetEnvironmentVariable("OPENLOAD_LOGIN", "<YOUR API LOGIN>", "User")
[Environment]::SetEnvironmentVariable("OPENLOAD_KEY", "<YOUR API KEY>", "User")
```

##### Extra
The **api key** and **api_login** can be found on [this page]("https://openload.co/account#usersettings")