import re

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


# Функция для нормализации названий с помощью fuzzy
def normalize_with_fuzzy(name, valid_names, threshold=60):
    # Используем process.extractOne для поиска наиболее похожего имени из списка
    if name[0] in valid_names:
        match = process.extractOne(name, valid_names[name[0]], scorer=fuzz.ratio)
        if match and match[1] >= threshold:  # Если найдено совпадение выше порога
            return match[0]
    else:
        valid_names[name[0]] = []
    valid_names[name[0]].append(name)
    return name  # Если совпадений нет, возвращаем исходное название


def remove_special_characters_for_organisation(text):
    # Убираем все символы, не являющиеся буквами, цифрами, пробелами
    text = text.replace('\n', '')
    text = re.sub(r'[^\w\s-]', '', text)
    # emoji.replace_emoji(text, '')
    return text


def remove_special_characters_for_location(text):
    # Убираем все символы, не являющиеся буквами, цифрами, пробелами
    text = text.replace('\n', '')
    text = re.sub(r'[^A-Za-zА-Яа-яЁё\s-]', '', text)
    # emoji.replace_emoji(text, '')
    return text


def parse_arr_for_normalize(row):
    no_added_elems = []
    for i in range(len(row)):
        if " - " in row[i]:
            elems = row[i].split(" - ")
            row[i] = elems[0]
            no_added_elems.extend(elems[1:])
    row.extend(no_added_elems)


# Применяем нормализацию для городов и организаций
def normalize_cities(row):
    parse_arr_for_normalize(row)
    for i in range(len(row)):
        row[i] = remove_special_characters_for_location(row[i])
        row[i] = row[i].capitalize()
    ans = []
    for i in range(len(row)):
        if row[i] != '':
            ans += [normalize_with_fuzzy(row[i], cities)]
    return ans


def normalize_organisations(row):
    parse_arr_for_normalize(row)
    for i in range(len(row)):
        row[i] = remove_special_characters_for_organisation(row[i])
        row[i] = row[i].capitalize()
    ans = []
    for i in range(len(row)):
        if row[i] != '':
            ans += [normalize_with_fuzzy(row[i], organisations)]
    return ans


# Применяем нормализацию по строкам
cities_df['normalized_cities'] = cities_df['cities'].apply(normalize_cities)
orgs_df['normalized_organisations'] = orgs_df['organisations'].apply(normalize_organisations)

# Теперь подсчитаем количество упоминаний городов и организаций
city_mentions = cities_df['normalized_cities'].explode().dropna()
org_mentions = orgs_df['normalized_organisations'].explode().dropna()

# Подсчитываем упоминания
city_counts = city_mentions.value_counts().head(20)
org_counts = org_mentions.value_counts().head(20)

# Строим графики
import matplotlib.pyplot as plt

# График по городам
plt.figure(figsize=(15, 20))
city_counts.plot(kind='bar')
plt.title('Популярные направления перевозок')
plt.xlabel('Город/Направление')
plt.ylabel('Количество упоминаний')
plt.xticks(rotation=90)
plt.show()

# График по организациям
plt.figure(figsize=(15, 20))
org_counts.plot(kind='bar')
plt.title('Рекламируемые организации')
plt.xlabel('Организация')
plt.ylabel('Количество упоминаний')
plt.xticks(rotation=90)
plt.show()

plt.close()