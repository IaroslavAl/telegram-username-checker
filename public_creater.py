from telethon.sync import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest

# Ваши данные
api_id = 1234567  # Замените на ваш API ID
api_hash = 'ваш_api_hash'  # Замените на ваш API Hash
phone_number = '+79991234567'  # Ваш номер телефона

# Названия каналов (можно прочитать из файла)
channel_names = [
    "Название канала 1",
    "Название канала 2",
    # ... и так далее
]

# Авторизация
client = TelegramClient('session_name', api_id, api_hash)
client.start(phone=phone_number)

for name in channel_names:
    try:
        # Создаём канал (паблик)
        result = client(CreateChannelRequest(
            title=name,
            about="Описание канала",
            megagroup=False,  # False = канал, True = супергруппа
        ))
        print(f"Канал '{name}' создан: https://t.me/{result.chats[0].username}")
    except Exception as e:
        print(f"Ошибка при создании '{name}': {e}")

client.disconnect()