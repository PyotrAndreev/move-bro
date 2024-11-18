import os
from pyrogram import Client, filters
from pyrogram.types import Message
import sqlite3


api_id = ""  # user api_id
api_hash = ""  # user api_has
admin_id = 0  # admin id

app = Client("my_account", api_id=api_id, api_hash=api_hash)

conn = sqlite3.connect("chat_links.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS chat_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link TEXT UNIQUE
                )""")
conn.commit()

async def send_messages(text):
    cursor.execute("SELECT link FROM chat_links")
    links = cursor.fetchall()
    for link in links:
        user_id = link[0]
        try:
            await app.send_message(user_id, text)
            print(f"Сообщение отправлено пользователю {user_id}")
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

# /send_all <message> - отправляет <message> всем из бд 
@app.on_message(filters.command("send_all") & filters.user(admin_id))
async def command_send_all(client, message):
    text = message.text.markdown[len("/send_all "):]
    print(text)
    await send_messages(text)
    await message.reply("Сообщения отправлены всем пользователям.")


# /add <user> - добавляет <user> в бд (+ проверка на )
@app.on_message(filters.command("add") & filters.user(admin_id))
async def add_user(client, message):
    user = message.text.markdown[len("/add "):].strip().lower()
    cursor.execute("SELECT COUNT(*) FROM chat_links WHERE link = ?", (user,))
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO chat_links (link) VALUES (?)", (user,))
        conn.commit()
        await message.reply(f"{user} добавлен в базу данных.")
    else:
        await message.reply(f"{user} уже есть в базе данных.")

# /remove <user>
@app.on_message(filters.command("remove") & filters.user(admin_id))
async def remove_user(client, message):
    user = message.text.markdown[len("/remove "):]
    cursor.execute("SELECT COUNT(*) FROM chat_links WHERE link = ?", (user,))
    if cursor.fetchone()[0] > 0:
        cursor.execute("DELETE FROM chat_links WHERE link = ?", (user,))
        conn.commit()
        await message.reply(f"{user} удален из базы данных.")
    else:
        await message.reply(f"{user} не найден в базе данных.")

# /show -> все юзеры в бд
@app.on_message(filters.command("show") & filters.user(admin_id))
async def show_all(client, message):
    cursor.execute("SELECT link FROM chat_links")
    links = cursor.fetchall()
    await message.reply('\n'.join(i[0] for i in links))
    print('\n'.join(i[0] for i in links))

# /get <user> - информация о <user>
@app.on_message(filters.command("get") & filters.user(admin_id))
async def get_user_info(client, message):
    try:
        # Получаем ID или юзернейм из команды
        args = message.text.split()
        if len(args) < 2:
            await message.reply("Пожалуйста, укажите ID или юзернейм пользователя.")
            return

        identifier = args[1]
        user = await app.get_users(identifier)
        info = (
            f"ID: {user.id}\n"
            f"Имя: {user.first_name or 'Не указано'}\n"
            f"Фамилия: {user.last_name or 'Не указана'}\n"
            f"Юзернейм: @{user.username if user.username else 'Не указан'}\n"
            f"Бот: {'Да' if user.is_bot else 'Нет'}\n"
            f"Язык интерфейса: {user.language_code or 'Неизвестен'}\n"
        )

        # Если это бот, добавить его описание
        if user.is_bot:
            info += f"Описание бота: {user.description or 'Нет описания'}\n"

        # Отправляем информацию
        await message.reply(info)

    except Exception as e:
        await message.reply(f"Ошибка: {e}")


app.run()