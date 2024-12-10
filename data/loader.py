from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties


def start_bot(token: str):
    # Initialize the bot with the updated default argument
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode="HTML")  # Set parse_mode here
    )
    return bot
