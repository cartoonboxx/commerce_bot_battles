from data import config
import urllib

def encode_url(account_id):
    base_url = 'https://t.me/share/url'
    bot_url = f'https://t.me/{config.bot_name}?start={account_id}'
    text = "👉 Привет, можешь пожалуйста проголосовать за меня в боте?"
    encoded_bot_url = urllib.parse.quote(bot_url, safe='')
    encoded_text = urllib.parse.quote(text, safe='')
    full_url = f"{base_url}?url={encoded_bot_url}&text={encoded_text}"
    return full_url