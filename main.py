from classes.telegrambot import TelegramBot
from config.params import Params

def main():
    bot = TelegramBot()
    bot.start_bot()

if __name__ == "__main__":
    main()