import aiohttp
import asyncio
from tqdm import tqdm
from names_dataset import NameDataset
from transliterate import translit

def get_names() -> list[str]:
    nd = NameDataset()
    country = 'AL'
    result = nd.get_top_names(n=10000, gender='Male', country_alpha2=country)
    names = result[country]['M']
    return names

async def check_username(session, username, results):
    # name = translit(username, "ru", reversed=True).replace("'", "")
    name = username

    # Пропускаем имена короче 5 символов
    if len(name) < 5:
        results[name] = "Слишком короткое (<5 символов)"
        return  # Выходим из функции

    url = f"https://t.me/{name}"
    try:
        async with session.get(url, allow_redirects=False) as response:
            if response.status == 200:
                results[name] = "Занято"
            elif response.status == 404:
                results[name] = "Свободно"
            else:
                results[name] = f"Ошибка: {response.status}"
    except Exception as e:
        results[name] = f"Ошибка запроса: {e}"

async def check_many_usernames(usernames, max_concurrent=50):
    results = {}
    connector = aiohttp.TCPConnector(limit_per_host=max_concurrent, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for username in usernames:
            task = asyncio.create_task(check_username(session, username, results))
            tasks.append(task)
        # Прогресс-бар (опционально)
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            await f
    return results

usernames = get_names()
results = asyncio.run(check_many_usernames(common_words))

with open("telegram_usernames.txt", "w") as f:
    for username, status in results.items():
        f.write(f"@{username}: {status}\n")

print("Проверка завершена. Результаты сохранены в telegram_usernames.txt")