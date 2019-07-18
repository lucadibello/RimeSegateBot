import os
from classes.telegrambot import TelegramBot
from classes.config import Config

# Main function.


def main():
    print_splashscreen()

    # Find the config file path and creates a config manager.
    config = config_loader()
    manager = Config(config)
    
    # Load settings
    settings = manager.get_settings()
    print("[!] Settings loaded correctly:")
    print_settings(settings)

    # Start the bot using the settings
    start_bot(settings)


def print_splashscreen():
    splash = \
    """
        (                  (                                           
    )\ )               )\ )                   )       (         )  
    (()/((     )     ( (()/(  (  (  (     ) ( /(  (  ( )\     ( /(  
    /(_))\   (     ))\ /(_))))\ )\))( ( /( )\())))\ )((_) (  )\()) 
    (_))((_)  )\  '/((_(_)) /((_((_))\ )(_)(_))//((_((_)_  )\(_))/  
    | _ \(_)_((_))(_)) / __(_))  (()(_((_)_| |_(_))  | _ )((_| |_   
    |   /| | '  \(/ -_)\__ / -_)/ _` |/ _` |  _/ -_) | _ / _ |  _|  
    |_|_\|_|_|_|_|\___||___\___|\__, |\__,_|\__\___| |___\___/\__|  
                                |___/                               

        By Luca Di Bello
            -> Email: luca.dibello@samtrevano.ch
            -> Telegram: @lucadibello
    """

    print(splash)


def print_settings(settings: dict):
    for key, value in settings.items():
        print("->", key, ":", value)

'''
This function tries to look for the config file by itself. If it doesn't find the 
file asks the user what to do:

1) Pass the config file path
2) Generate a new file path

This method returns the config file path.
'''


def config_loader() -> str:
    possible_path = "config/config.json"

    if os.path.isfile(possible_path):
        return possible_path
    else:
        print("I coudn't find the config file. What you wanna do?")
        question = " 1) Generate a new file \n 2) Insert the config file path"
        _asker(question)

# This method is used for requesting an input from the user.


def _asker(question: str):
    print("TODO")

# This function is used to start the bot.


def start_bot(config: dict):
    # Start bot
    bot = TelegramBot(config)
    bot.start_bot()


if __name__ == "__main__":
    main()
