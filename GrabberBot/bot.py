import os
from pyrogram import Client, filters
from pyrogram.types import Message
import sqlite3
from datetime import datetime, timedelta
from grabber import grab_ents, msgs_filtering
# Настройки клиента. Замените api_id и api_hash своими данными.
api_id = "3065049"
api_hash = "fd612fdda418b6f1ce40fd6d41229622"
admin_id = 840618032 # ID администратора.
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
        cities TEXT,
        timestamp DATETIME
    )
""")
conn.commit()


# Обработчик команды /start
@app.on_message(filters.command("start", prefixes="#"))
def start_command(client, message):
    message.reply_text(
        f"Привет! Я помощник для рассылки сообщений в групповые чаты. "
        f"Отправьте мне ссылку на чат, чтобы добавить его в базу данных. "
        f"Твой userid: {message.from_user.id}\n"
        f"Ну и справочка по моим командам:\n"
        f"#get_msgs chat_id - сохраняет последние 100 сообщений в заданном чате и обрабатывает их\n"
        f"<ссылка_на_чат> - я попробую вступить в чат и сохранить, обработать сообщения из него"
    )


# Функция для удаления сообщений старше двух недель
def delete_old_messages():
    two_weeks_ago = datetime.now() - timedelta(weeks=2)
    cursor.execute("DELETE FROM chat_messages WHERE timestamp < ?", (two_weeks_ago,))
    conn.commit()


# Функция для загрузки и сохранения истории сообщений чата
def save_chat_history(client, chat_id):
    print("Зашёл")
    try:
        # Загружаем последние сообщения (до 100 сообщений)
        for message in client.get_chat_history(chat_id, limit=100):
            if message.text: # Проверка, что сообщение текстовое
                # ents_label - название сущности, можно посмотреть в доке spacy (ORG, LOC, PER и тд)
                ents = grab_ents(message.text.markdown, "LOC")
                cursor.execute(
                    "INSERT INTO chat_messages (chat_id, message_text,cities, timestamp) VALUES (?, ?, ?, ?)",
                    (chat_id, message.text, str(ents), message.date)
                )
                if len(ents) != 0:
                    print("Города:", ents, "Сообщение:", message.text)
        conn.commit()
        print(f"История сообщений для чата {chat_id} успешно сохранена.")
    except Exception as e:
        print(f"Ошибка при сохранении истории чата {chat_id}: {str(e)}")
@app.on_message(filters.command("get_msgs", prefixes="#"))
def get_msgs(client, message):
    chat_id = int(message.text.markdown[len("#get_msgs "):])
    save_chat_history(client, chat_id)
#relevant_get chat_id filter_word ent
@app.on_message(filters.command("relevant_get", prefixes="#"))
def relevant_get(client, message):
    parameters = message.text.markdown.split(' ')
    chat_id = int(parameters[1])
    filter_word = parameters[2]
    ent = parameters[3]
    msgs = []
    try:
        # Загружаем последние сообщения (до 100 сообщений)
        for message in client.get_chat_history(chat_id, limit=100):
            if message.text: # Проверка, что сообщение текстовое
                msgs.append(message.text.markdown)
    except Exception as e:
        print(f"Ошибка при сохранении истории чата {chat_id}: {str(e)}")
    print(len(msgs))
    information = msgs_filtering(msgs, filter_word, ent)
    for el_info in information:
        if len(el_info[0])>0:
            print(el_info[0])
            cursor.execute(
                "INSERT INTO chat_messages (chat_id, message_text,cities, timestamp) VALUES (?, ?, ?, ?)",
                (chat_id, el_info[1],str(el_info[0]), message.date)
            )
    conn.commit()
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
        message.reply_text(f"Произошла ошибка: {e}")

# Обработчик получения новых сообщений в добавленных чатах
@app.on_message(filters.all)
def save_message(client, message: Message):
    chat_id = message.chat.id
    message_text = message.text or ""  # Проверка, если текстовое сообщение пустое
    # Сохранение сообщения с отметкой времени
    ents = grab_ents(message.text.markdown, "LOC")
    if len(ents) > 0:
        cursor.execute("INSERT INTO chat_messages (chat_id, message_text,cities, timestamp) VALUES (?, ?, ?, ?)",
                       (chat_id, message_text,str(ents), datetime.now()))
        conn.commit()
    client.send_message(admin_id, f"message_text:{message_text}, chat_id:{chat_id}, datetime:{datetime.now()}")

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
        message.reply_text(f"{chat_id}")
        try:
            client.send_message(chat_id, text)
            # client.leave_chat(chat_link)
        except Exception as e:
            message.reply_text(f"Ошибка при отправке сообщения в чат {chat_link}: {str(e)}")
            trouble_sending = True
    message.reply_text(
        f"Сообщение успешно отправлено!{'' if not trouble_sending else ' Но были проблемы с отправкой в некоторые чаты'}")


# Запуск клиента пользователя
app.run()