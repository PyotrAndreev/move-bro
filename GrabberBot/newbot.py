import os
from pyrogram import Client, filters
from pyrogram.types import Message
import sqlite3
from datetime import datetime
import re
from grabber import grab_ents

# ====================
# Bot для сохранения сообщений, извлечения маршрутов и NER-анализа
# Сохраняет в SQLite-файл chat_data.db таблицы:
#   • chat_links(link)
#   • chat_messages(id, chat_id, message_id, text, timestamp)
#   • shipments(id, chat_id, message_id, src, dst, item, timestamp)
#   • chat_messages_location(id, chat_id, message_id, text, locations, timestamp)
#   • chat_messages_organisations(id, chat_id, message_id, text, organisations, timestamp)
# ====================

# Настройки Pyrogram
api_id = os.getenv("API_ID", "9093213")
api_hash = os.getenv("API_HASH", "7a586baf41613d2d93da8333d3446832")
admin_id = int(os.getenv("ADMIN_ID", "5047922581"))
app = Client("my_user", api_id, api_hash)

# Предел по количеству сообщений (например, 5000)
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", "5000"))

# Подключение к базе
conn = sqlite3.connect("chat_data.db", check_same_thread=False)
cursor = conn.cursor()

# Создание таблиц с уникальными ограничениями
cursor.executescript("""
CREATE TABLE IF NOT EXISTS chat_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    link TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    message_id INTEGER,
    text TEXT,
    timestamp DATETIME,
    UNIQUE(chat_id, message_id)
);

CREATE TABLE IF NOT EXISTS shipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    message_id INTEGER,
    src TEXT,
    dst TEXT,
    item TEXT,
    timestamp DATETIME,
    UNIQUE(chat_id, message_id)
);

CREATE TABLE IF NOT EXISTS chat_messages_location (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    message_id INTEGER,
    text TEXT,
    locations TEXT,
    timestamp DATETIME,
    UNIQUE(chat_id, message_id)
);

CREATE TABLE IF NOT EXISTS chat_messages_organisations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    message_id INTEGER,
    text TEXT,
    organisations TEXT,
    timestamp DATETIME,
    UNIQUE(chat_id, message_id)
);
""")
conn.commit()

# Пагинация по всей истории чата

def iter_all_messages(client, chat_id, batch_size=1000):
    last_id = 0
    while True:
        batch = list(client.get_chat_history(chat_id, limit=batch_size, offset_id=last_id))
        if not batch:
            break
        for msg in batch:
            yield msg
        last_id = batch[-1].id

# Функция сохранения сообщений, извлечения маршрутов и NER

def save_chat_history(client, chat_id):
    processed = 0
    for message in iter_all_messages(client, chat_id):
        raw_text = getattr(message, 'text', None)
        if not raw_text:
            continue
        processed += 1
        if processed > MAX_MESSAGES:
            break

        text = str(raw_text)  # Приводим к Python str для совместимости с grab_ents и regex
        ts = message.date
        msg_id = message.id

        # Сохраняем сырое сообщение
        cursor.execute(
            "INSERT OR IGNORE INTO chat_messages(chat_id, message_id, text, timestamp) VALUES (?, ?, ?, ?)",
            (chat_id, msg_id, text, ts)
        )

        # NER: локации и организации
        ents_loc = grab_ents(text, "LOC")
        if ents_loc:
            cursor.execute(
                "INSERT OR IGNORE INTO chat_messages_location(chat_id, message_id, text, locations, timestamp) VALUES (?, ?, ?, ?, ?)",
                (chat_id, msg_id, text, ",".join(map(str, ents_loc)), ts)
            )
        ents_org = grab_ents(text, "ORG")
        if ents_org:
            cursor.execute(
                "INSERT OR IGNORE INTO chat_messages_organisations(chat_id, message_id, text, organisations, timestamp) VALUES (?, ?, ?, ?, ?)",
                (chat_id, msg_id, text, ",".join(map(str, ents_org)), ts)
            )

        # Паттерн маршрута "из X в Y"
        m = re.search(r'(?:из|от)\s+([\w\-]+)\s+(?:в|до)\s+([\w\-]+)', text, flags=re.IGNORECASE)
        if m:
            src, dst = m.group(1), m.group(2)
            item_match = re.search(r'отправля[ею]\s+([\w\s\-]+?)(?:\s+из|\s+в|$)', text, flags=re.IGNORECASE)
            item = item_match.group(1).strip() if item_match else None
            cursor.execute(
                "INSERT OR IGNORE INTO shipments(chat_id, message_id, src, dst, item, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (chat_id, msg_id, src, dst, item, ts)
            )
        conn.commit()

# Команда добавления ссылки на чат
@app.on_message(filters.user(admin_id) & filters.command("add_chat", prefixes="#"))
def add_chat(client, message):
    link = str(message.text.split(maxsplit=1)[1])
    cursor.execute("INSERT OR IGNORE INTO chat_links(link) VALUES (?)", (link,))
    conn.commit()
    message.reply_text(f"Чат {link} добавлен.")

# Триггер для ручного запуска сбора по всем чатам
@app.on_message(filters.user(admin_id) & filters.command("collect", prefixes="#"))
def collect_all(client, message):
    cursor.execute("SELECT link FROM chat_links")
    for (link,) in cursor.fetchall():
        try:
            chat = client.join_chat(str(link))
            save_chat_history(client, chat.id)
        except Exception as e:
            message.reply_text(f"Ошибка в {link}: {e}")
    message.reply_text(f"Сбор завершён. Обработано до {MAX_MESSAGES} сообщений на чат.")

# Запуск клиента
app.run()
