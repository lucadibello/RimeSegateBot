from classes.telegrambot import TelegramBot
from config.params import Params
from classes.config import Config

'''
Main function.
'''
def main():
    manager = Config("config/config.json")


'''
    This function is used to start the bot.
'''
def _start_bot():
    ''' Start bot '''
    bot = TelegramBot()
    bot.start_bot()

if __name__ == "__main__":
    main()