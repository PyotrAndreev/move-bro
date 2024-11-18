import os
from pyrogram import Client, filters
from pyrogram.types import Message
import sqlite3

# Настройки клиента. Замените api_id и api_hash своими данными(можно взять в https://my.telegram.org/apps)
api_id = "api_id_here"
api_hash = "api_hash_here"
# ID администратора, который может использовать команды /send и /add, можно посмотреть в https://t.me/getmyid_bot, также его отправляет бот при команде /start
# admin_id = admin_id_here

# Создание клиента пользователя
app = Client("my_user", api_id, api_hash)

# Создание базы данных для хранения ссылок на чаты
conn = sqlite3.connect("chat_links.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS chat_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link TEXT
                )""")
conn.commit()

# Обработчик команды /start
@app.on_message(filters.command("start"))
def start_command(client, message):
    message.reply_text(f"Привет! Я помощник для рассылки сообщений в групповые чаты. Отправьте мне ссылку на чат, чтобы добавить его в базу данных. Твой userid:{message.from_user.id}")
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
            #client.leave_chat(chat_link)
        except Exception as e:
            message.reply_text(f"Ошибка при отправке сообщения в чат {chat_link}: {str(e)}")
            trouble_sending = True
    message.reply_text(f"Сообщение успешно отправлено!{'' if not trouble_sending else 'Но были проблемы с отправкой в некоторые чаты'}")

# Обработчик получения ссылки на чат от админа
@app.on_message(filters.user(admin_id) & filters.regex(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'))
def add_chat_link(client, message):
    link = message.text
    print("here")
    cursor.execute("INSERT INTO chat_links (link) VALUES (?)", (link,))
    conn.commit()
    message.reply_text("Ссылка на чат успешно добавлена в базу данных!")

# Запуск клиента пользователя
app.run()
