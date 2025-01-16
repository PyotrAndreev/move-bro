import re
import aiohttp
import asyncio
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Загрузка данных из CSV файлов
chats_df = pd.read_csv('chat_links.csv')
cities_df = pd.read_csv('chat_messages_location.csv')
orgs_df = pd.read_csv('chat_messages_organisations.csv')

cities_df['cities'] = cities_df['cities'].apply(lambda x: eval(x) if isinstance(x, str) else [])
orgs_df['organisations'] = orgs_df['organisations'].apply(lambda x: eval(x) if isinstance(x, str) else [])

# Список городов и организаций для нормализации
cities = dict()
organisations = dict()

# Кэширование результатов
city_cache = dict([("Америку", False)])
org_cache = dict([("Снг", False), ("Оплата", False), ("Связи", False), ("Мб", False)])

# Асинхронная проверка, является ли название городом
async def is_city_name(session, query, retries=3):
    if query in city_cache:
        return city_cache[query]

    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "format": "json"
    }
    for attempt in range(retries):
        try:
            async with session.get(url, params=params) as response:
                if response.status == 429:  # Превышен лимит запросов
                    await asyncio.sleep(1)  # Ждём перед повтором
                    continue
                response.raise_for_status()
                data = await response.json()
                for result in data.get("search", []):
                    description = result.get("description", "").lower()
                    if "town" in description or "cit" in description:
                        city_cache[query] = True
                        return True
        except Exception as e:
            print(f"Попытка {attempt + 1} для {query} завершилась ошибкой: {e}")
            await asyncio.sleep(2)
    city_cache[query] = False
    return False


# Асинхронная проверка, является ли название организацией
async def is_organization_name(session, query, retries=3):
    if query in org_cache:
        return org_cache[query]

    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "format": "json"
    }
    for attempt in range(retries):
        try:
            async with session.get(url, params=params) as response:
                if response.status == 429:  # Превышен лимит запросов
                    await asyncio.sleep(1)  # Ждём перед повтором
                    continue
                response.raise_for_status()
                data = await response.json()
                for result in data.get("search", []):
                    description = result.get("description", "").lower()
                    if "compan" in description or "organization" in description or "corporation" in description:
                        org_cache[query] = True
                        return True
        except Exception as e:
            print(f"Попытка {attempt + 1} для {query} завершилась ошибкой: {e}")
            await asyncio.sleep(2)
    org_cache[query] = False
    return False


# Асинхронная фильтрация
async def filter_async(df_column, check_function):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for item in df_column:
            tasks.append(check_function(session, item))
        results = await asyncio.gather(*tasks)
    return df_column[results]


# Функции нормализации
def normalize_with_fuzzy(name, valid_names, threshold=60):
    if name[0] in valid_names:
        match = process.extractOne(name, valid_names[name[0]], scorer=fuzz.ratio)
        if match and match[1] >= threshold:
            return match[0]
    else:
        valid_names[name[0]] = []
    valid_names[name[0]].append(name)
    return name


def remove_special_characters(text, is_location=True):
    text = text.replace('\n', '')
    if is_location:
        return re.sub(r'[^A-Za-zА-Яа-яЁё\s-]', '', text)
    return re.sub(r'[^\w\s-]', '', text)


def parse_arr_for_normalize(row):
    no_added_elems = []
    for i in range(len(row)):
        if " - " in row[i]:
            elems = row[i].split(" - ")
            row[i] = elems[0]
            no_added_elems.extend(elems[1:])
    row.extend(no_added_elems)


def normalize(row, valid_names, is_location=True):
    parse_arr_for_normalize(row)
    for i in range(len(row)):
        row[i] = remove_special_characters(row[i], is_location=is_location)
        row[i] = row[i].capitalize()
    ans = []
    for i in range(len(row)):
        if row[i] != '':
            ans += [normalize_with_fuzzy(row[i], valid_names)]
    return ans


cities_df['normalized_cities'] = cities_df['cities'].apply(lambda x: normalize(x, cities, is_location=True))
orgs_df['normalized_organisations'] = orgs_df['organisations'].apply(lambda x: normalize(x, organisations, is_location=False))


# Асинхронная обработка данных
async def main():
    city_mentions = cities_df['normalized_cities'].explode().dropna()
    org_mentions = orgs_df['normalized_organisations'].explode().dropna()

    cities_filtered = await filter_async(city_mentions, is_city_name)
    org_filtered = await filter_async(org_mentions, is_organization_name)

    city_counts = cities_filtered.value_counts().head(20)
    org_counts = org_filtered.value_counts().head(20)

    # Построение графиков
    import matplotlib.pyplot as plt

    plt.figure(figsize=(15, 20))
    city_counts.plot(kind='bar')
    plt.title('Популярные направления перевозок')
    plt.xlabel('Город/Направление')
    plt.ylabel('Количество упоминаний')
    plt.xticks(rotation=90)
    plt.show()

    plt.figure(figsize=(15, 20))
    org_counts.plot(kind='bar')
    plt.title('Рекламируемые организации')
    plt.xlabel('Организация')
    plt.ylabel('Количество упоминаний')
    plt.xticks(rotation=90)
    plt.show()


if __name__ == "__main__":
    asyncio.run(main())