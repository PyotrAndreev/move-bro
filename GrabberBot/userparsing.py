import os
import sqlite3
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw import functions
from sqlalchemy import except_
import asyncio
from grabber import grab_ents
from datetime import datetime
from time import sleep
from tqdm import tqdm


api_id = int(os.getenv("API_ID", ""))
api_hash = os.getenv("API_HASH", "")
admin_id = int(os.getenv("ADMIN_ID", ""))
app = Client("my_user", api_id, api_hash)

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", "1000000"))

conn = sqlite3.connect("chat_data.db", check_same_thread=False)
cursor = conn.cursor()

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
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    bio TEXT,
    last_seen DATETIME
);
""")
conn.commit()

class BioCache:
    def __init__(self, app: Client):
        self.app = app
        self.cache = {}

    async def get_bio(self, user_id: int) -> str:
        if user_id in self.cache:
            return self.cache[user_id]

        try:
            full_user = await self.app.invoke(
                functions.users.GetFullUser(
                    id=await self.app.resolve_peer(user_id)
                )
            )
            bio = full_user.full_user.about or ""
            self.cache[user_id] = bio
            return bio
        except Exception as e:
            print(f"Ошибка получения био для {user_id}: {e}")
            return ""

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
    bio_cache = BioCache(app)
    try:
        with tqdm(total=len(messages), desc="Обработка сообщений") as pbar:
            async for message in messages:
                if not isinstance(message, Message) or not message.from_user:
                    continue

                user = message.from_user
                full_name = user.first_name
                if user.last_name:
                    full_name += " " + user.last_name

                bio = await bio_cache.get_bio(user.id)

                data = (
                    message.text or "",
                    message.date,
                    full_name,
                    user.id,
                    user.username or "",
                    bio,
                    message.id
                )

                try:
                    cursor.execute('''INSERT OR IGNORE INTO messages 
                                       (message_text, date, sender_name, sender_id, 
                                        sender_username, sender_bio, message_id)
                                       VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
                    pbar.update(1)
                except Exception as e:
                    print(f"Ошибка записи: {e}")

                await asyncio.sleep(0.1)

        conn.commit()
        print(f"\nВсего уникальных пользователей: {len(bio_cache.cache)}")

    except Exception as e:
        print(f"\nФатальная ошибка: {e}")

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
                await asyncio.sleep(600)
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
