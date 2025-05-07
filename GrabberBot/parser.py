import os
import sqlite3
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from sqlalchemy import except_
from asyncio import sleep
from grabber import grab_ents
from datetime import datetime
from time import sleep

# ====================
# Round-robin бот для поочередной обработки чатов батчами по 1000 сообщений
# + автоматическое добавление новых ссылок из сообщений внутри process_batch
# ====================

# Настройки Pyrogram
api_id = int(os.getenv("API_ID", "9093213"))
api_hash = os.getenv("API_HASH", "7a586baf41613d2d93da8333d3446832")
admin_id = int(os.getenv("ADMIN_ID", "5047922581"))
app = Client("my_user", api_id, api_hash)

# Параметры
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", "1000000"))

# Подключение к БД
conn = sqlite3.connect("chat_data.db", check_same_thread=False)
cursor = conn.cursor()

# Создание таблиц
cursor.executescript("""
CREATE TABLE IF NOT EXISTS chat_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    link TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS chat_progress (
    chat_id INTEGER PRIMARY KEY,
    last_message_id INTEGER DEFAULT 0,
    processed_count INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    message_id INTEGER,
    text TEXT,
    timestamp DATETIME,
    sender_id INTEGER,
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
    sender_id INTEGER,
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

CREATE TABLE IF NOT EXISTS found_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    link TEXT UNIQUE
);
""")
conn.commit()

# Паттерн для ссылок на группы
link_pattern = re.compile(r"(t\.me/[A-Za-z0-9_]+|@[A-Za-z0-9_]+)")

# Функция добавления ссылки в базу и инициализации прогресса
async def add_link_to_parsing(link, client):
    cursor.execute("SELECT 1 FROM chat_links WHERE link = ?", (link,))
    if cursor.fetchone():
        return
    try:
        new_chat = await client.get_chat(link)
        if str(new_chat.type) not in ["ChatType.GROUP", "ChatType.SUPERGROUP"]:
            return
        cursor.execute("INSERT INTO chat_links(link) VALUES(?)", (link,))
        new_chat = await client.join_chat(link)
        cursor.execute("INSERT OR IGNORE INTO chat_progress(chat_id) VALUES(?)", (new_chat.id,))
        conn.commit()
        print(f"Добавлен чат для парсинга: {link}")
    except Exception as e:
        print(f"Ошибка при добавлении ссылки {link}: {e}")

# Обрабатывает один батч сообщений для указанного чата
async def process_batch(chat_id, messages, client):
    for message in messages:
        raw_text = getattr(message, 'text', '')
        if not raw_text:
            continue
        text = str(raw_text)
        ts = message.date
        msg_id = message.id
        sender_id = message.from_user.id if message.from_user else 0

        # 1) Авто-добавление ссылок внутри process_batch
        for m in link_pattern.finditer(text):
            link = m.group(0)
            # await add_link_to_parsing(link, client)
            print(link)
            cursor.execute(
                "INSERT OR IGNORE INTO found_links(link) VALUES(?)",
                (link,)
            )
        # 2) Сохранение сообщения
        cursor.execute(
            "INSERT OR IGNORE INTO chat_messages(chat_id,message_id,text,timestamp,sender_id) VALUES(?,?,?,?,?)",
            (chat_id, msg_id, text, ts, sender_id)
        )
        # 3) NER-локации
        ents_loc = grab_ents(text, "LOC")
        if ents_loc:
            cursor.execute(
                "INSERT OR IGNORE INTO chat_messages_location(chat_id,message_id,text,locations,timestamp,sender_id) VALUES(?,?,?,?,?,?)",
                (chat_id, msg_id, text, ",".join(ents_loc), ts, sender_id)
            )
        # 4) NER-организации
        ents_org = grab_ents(text, "ORG")
        if ents_org:
            cursor.execute(
                "INSERT OR IGNORE INTO chat_messages_organisations(chat_id,message_id,text,organisations,timestamp) VALUES(?,?,?,?,?)",
                (chat_id, msg_id, text, ",".join(ents_org), ts)
            )
        # 5) Маршрут отправки
        route = re.search(r'(?:из|от)\s+([\w\-]+)\s+(?:в|до)\s+([\w\-]+)', text, flags=re.IGNORECASE)
        if route:
            src, dst = route.group(1), route.group(2)
            item_match = re.search(r'отправля[ею]\s+([\w\s\-]+?)(?:\s+из|\s+в|$)', text, flags=re.IGNORECASE)
            item = item_match.group(1).strip() if item_match else None
            cursor.execute(
                "INSERT OR IGNORE INTO shipments(chat_id,message_id,src,dst,item,timestamp) VALUES(?,?,?,?,?,?)",
                (chat_id, msg_id, src, dst, item, ts)
            )
    conn.commit()

# Инициализация и round-robin сбор
@app.on_message(filters.user(admin_id) & filters.command("collect", prefixes="#"))
async def collect_all(client, message: Message):

    # Инициализируем прогресс для существующих ссылок
    cursor.execute("SELECT link FROM chat_links")
    links = [r[0] for r in cursor.fetchall()]
    for link in links:
        chat = await client.join_chat(link)
        cursor.execute("INSERT OR IGNORE INTO chat_progress(chat_id) VALUES(?)", (chat.id,))
    conn.commit()

    # Обрабатываем по батчам в round-robin
    while True:
        cursor.execute("SELECT chat_id, last_message_id, processed_count FROM chat_progress")
        rows = cursor.fetchall()
        did_any = False
        for chat_id, last_id, count in rows:
            if count >= MAX_MESSAGES:
                continue
            # batch = list(client.get_chat_history(chat_id, limit=BATCH_SIZE, offset_id=last_id))
            try:
                batch = []
                async for msg in client.get_chat_history(chat_id, limit=BATCH_SIZE, offset_id=last_id):
                    batch.append(msg)
            except Exception as e:
                print("Expection:", e)
                await sleep(600)
                continue
            if not batch:
                continue
            await process_batch(chat_id, batch, client)
            new_last = batch[-1].id
            new_count = count + len(batch)
            cursor.execute(
                "UPDATE chat_progress SET last_message_id=?, processed_count=? WHERE chat_id=?",
                (new_last, new_count, chat_id)
            )
            conn.commit()
            did_any = True
        if not did_any:
            break
    await message.reply_text("Сбор завершён для всех чатов.")

# Команда добавления чата
@app.on_message(filters.user(admin_id) & filters.command("add_chat", prefixes="#"))
def add_chat(_, message: Message):
    link = message.text.split(maxsplit=1)[1]
    cursor.execute("INSERT OR IGNORE INTO chat_links(link) VALUES(?)", (link,))
    conn.commit()
    message.reply_text(f"Чат {link} добавлен в очередь.")

# Запуск
if __name__ == '__main__':
    app.run()
