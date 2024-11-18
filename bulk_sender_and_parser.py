import os
from pyrogram import Client, filters
from pyrogram.types import Message
import sqlite3
from datetime import datetime, timedelta

# Настройки клиента. Замените api_id и api_hash своими данными.
api_id = "api_id_here"
api_hash = "api_hash_here"
admin_id = "admin_id_here"  # ID администратора.

# Создание клиента пользователя
app = Client("my_user", api_id, api_hash)

# Создание базы данных для хранения ссылок на чаты и сообщений
conn = sqlite3.connect("chat_data.db", check_same_thread=False)
cursor = conn.cursor()

# Таблица для ссылок на чаты
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link TEXT
    )
""")
# Таблица для сообщений с отметкой времени
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        message_text TEXT,
        timestamp DATETIME
    )
""")
conn.commit()

# Обработчик команды /start
@app.on_message(filters.command("start"))
def start_command(client, message):
    message.reply_text(
        f"Привет! Я помощник для рассылки сообщений в групповые чаты. "
        f"Отправьте мне ссылку на чат, чтобы добавить его в базу данных. "
        f"Твой userid: {message.from_user.id}"
    )

# Функция для удаления сообщений старше двух недель
def delete_old_messages():
    two_weeks_ago = datetime.now() - timedelta(weeks=2)
    cursor.execute("DELETE FROM chat_messages WHERE timestamp < ?", (two_weeks_ago,))
    conn.commit()

# Функция для загрузки и сохранения истории сообщений чата
def save_chat_history(client, chat_id):
    try:
        # Загружаем последние сообщения (до 100 сообщений)
        for message in client.get_chat_history(chat_id, limit=100):
            if message.text:  # Проверка, что сообщение текстовое
                cursor.execute(
                    "INSERT INTO chat_messages (chat_id, message_text, timestamp) VALUES (?, ?, ?)",
                    (chat_id, message.text, message.date)
                )
        conn.commit()
        print(f"История сообщений для чата {chat_id} успешно сохранена.")
    except Exception as e:
        print(f"Ошибка при сохранении истории чата {chat_id}: {str(e)}")

# Обработчик получения ссылки на чат от админа
@app.on_message(filters.user(admin_id) & filters.regex(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'))
def add_chat_link(client, message):
    link = message.text
    cursor.execute("INSERT INTO chat_links (link) VALUES (?)", (link,))
    conn.commit()
    message.reply_text("Ссылка на чат успешно добавлена в базу данных!")
    
    # Получение ID чата и сохранение истории сообщений после добавления ссылки
    try:
        chat = client.join_chat(link)
        save_chat_history(client, chat.id)
    except Exception as e:
        message.reply_text(f"Не удалось сохранить историю для чата {link}: {str(e)}")

# Обработчик получения новых сообщений в добавленных чатах
@app.on_message(filters.chat)
def save_message(client, message: Message):
    chat_id = message.chat.id
    message_text = message.text or ""  # Проверка, если текстовое сообщение пустое

    # Сохранение сообщения с отметкой времени
    cursor.execute("INSERT INTO chat_messages (chat_id, message_text, timestamp) VALUES (?, ?, ?)",
                   (chat_id, message_text, datetime.now()))
    conn.commit()

    # Удаление старых сообщений после вставки нового
    delete_old_messages()

# Обработчик команды /send для рассылки сообщения
@app.on_message(filters.user(admin_id) & filters.command("send"))
def send_message(client, message):
    text = message.text.markdown[len("/send "):]
    cursor.execute("SELECT link FROM chat_links")
    links = cursor.fetchall()
    trouble_sending = False

    for link in links:
        chat_link = link[0]
        try:
            client.join_chat(chat_link)
        except Exception as exc:
            message.reply_text(f"Ошибка при входе в чат {chat_link}: {str(exc)}")
        chat_id = client.get_chat(chat_link).id
        try:
            client.send_message(chat_id, text)
            # client.leave_chat(chat_link)
        except Exception as e:
            message.reply_text(f"Ошибка при отправке сообщения в чат {chat_link}: {str(e)}")
            trouble_sending = True
    message.reply_text(f"Сообщение успешно отправлено!{'' if not trouble_sending else ' Но были проблемы с отправкой в некоторые чаты'}")

# Запуск клиента пользователя
app.run()
