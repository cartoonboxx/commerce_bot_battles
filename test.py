import urllib.parse

account_id = '38'  # Замените это на ваш фактический ID

# Основная ссылка для шаринга в Telegram
base_url = 'https://t.me/share/url'

# Ссылка на бот с вашим ID
bot_url = f'https://t.me/photobattllehelper_bot?start={account_id}'





# Текст, который вы хотите отправить
text = "👉 Привет, можешь пожалуйста проголосовать за меня в боте?"

# Кодируем каждый параметр отдельно
encoded_bot_url = urllib.parse.quote(bot_url, safe='')
encoded_text = urllib.parse.quote(text, safe='')

# Создаём полную ссылку
full_url = f"{base_url}?url={encoded_bot_url}&text={encoded_text}"

# Выводим полученную ссылку
print(full_url)