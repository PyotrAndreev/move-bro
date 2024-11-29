from email import message_from_bytes

from pyrogram import Client, filters
from pyrogram.types import Message
from database import get_db, Bots, Chats, Messages, Users
from sqlalchemy.orm import Session
from pytz import timezone
import pytz


api_id = ""
api_hash = ""
admin_id = 0
username = 'bot_username'
app = Client("my_account", api_id=api_id, api_hash=api_hash)

session = next(get_db())
print(len(session.query(Chats).all()))

@app.on_message(filters.command("start"))
def start_command(client, message):
    message.reply_text(f"Бот работает. Твой userid: {message.from_user.id}")

async def send_messages(client, message, text):
    chats = session.query(Chats).filter(Chats.bot_username == username).all()
    for chat in chats:
        chat_id = chat.chat_username
        chat_type = chat.type
        if (chat_type != 'dm'):
            try:
                client.join_chat(chat_id)
            except Exception as exc:
                message.reply_text(f"Ошибка при входе в чат {chat_id}: {str(exc)}")
        try:
            await app.send_message(chat_id, text)
            time = message.date.astimezone(timezone("Europe/Moscow"))
            session.add(Messages(chat_type=chat_type, chat_name=message.chat.username, message_id=message.id, user_username=chat_id, bot_username=username, content=message.text, date=time))
            session.commit()
            print(f"Сообщение отправлено {chat_id}")
        except Exception as e:
            print(f"Ошибка при отправке сообщения {chat_id}: {e}")

@app.on_message(filters.command("send_all") & filters.user(admin_id))
async def command_send_all(client, message):
    text = message.text.markdown[len("/send_all "):]
    print(text)
    await send_messages(client, message, text)
    await message.reply("Сообщения отправлены всем пользователям.")

@app.on_message(filters.command("add") & filters.user(admin_id))
async def add_user(client, message):
    user = message.text.markdown[len("/add "):].strip().lower()
    if (user[0] != '@'):
        await message.reply(f'Формат: @user')
    else:
        print(user[1:])
        try:
            chat_type = await app.get_chat(user[1:])
            # chat_type = chat_type.type
            check = session.query(Chats).filter_by(chat_username=user[1:]).first()
            if (str(chat_type.type)[9:] == "PRIVATE" and not check):
                session.add(Chats(type='dm', chat_username=user[1:], chat_id=chat_type.id, bot_username=username))
                session.commit()
                session.add(Users(username = user[1:], tg_id=chat_type.id, name=chat_type.first_name, lastname=chat_type.last_name))
                session.commit()
                # print(user[1:], chat_type.id, chat_type.first_name, chat_type.last_name)
                await message.reply(f'{user} добавлен')
            elif (str(chat_type.type)[9:] == "SUPERGROUP" and not check):
                session.add(Chats(type='group', chat_username=user[1:], chat_id=chat_type.id, bot_username=username))
                session.commit()
                await message.reply(f'{user} добавлен')
            else:
                await message.reply('Чат уже есть в базу')
        except Exception as e:
            await message.reply(f"Неверный юзернейм. {str(e)}")

@app.on_message(filters.command("remove") & filters.user(admin_id))
async def remove_user(client, message):
    user = message.text.markdown[len("/remove "):].strip().lower()
    if (user[0] != '@'):
        await message.reply(f'Формат: @user')
    else:
        print(user[1:])
        try:
            check = session.query(Chats).filter_by(chat_username=user[1:]).first()
            if (check):
                session.delete(check)
                session.commit()
                print(len(session.query(Chats).all()))
                await message.reply(f'{user} удален из базы')
            else:
                await message.reply('Чата нет в базе')
        except Exception as e:
            await message.reply(f"Неверный юзернейм. {str(e)}")

@app.on_message(filters.command("show") & filters.user(admin_id))
async def show_all(client, message):
    names = [f'@{i.chat_username} - type: {i.type}' for i in session.query(Chats).all()]
    await message.reply('\n'.join(names))
    print('\n'.join(names))

@app.on_message()
async def other(client, message):
    time = message.date.astimezone(timezone("Europe/Moscow"))
    check = session.query(Chats).filter_by(chat_username=message.chat.username).first()
    if not check:
        try:
            chat_username = message.chat.username
            chat_type = await app.get_chat(chat_username)
            # chat_type = chat_type.type
            check = session.query(Chats).filter_by(chat_username=chat_username).first()
            if (str(chat_type.type)[9:] == "PRIVATE" and not check):
                session.add(Chats(type='dm', chat_username=chat_username, chat_id=chat_type.id, bot_username=username))
                session.commit()
                print("Добавление нового dm")
            elif (str(chat_type.type)[9:] == "SUPERGROUP" and not check):
                session.add(Chats(type='group', chat_username=chat_username, chat_id=chat_type.id, bot_username=username))
                session.commit()
                print("Добавление нового group")
            else:
                print('Чат уже есть в базу')
        except Exception:
            print(f"Неверный юзернейм.")
    check = session.query(Chats).filter_by(chat_username=message.chat.username).first()
    if (check and message.text != None):
        if check.type == 'dm':
            session.add(Messages(chat_type=check.type, chat_name=message.chat.username, message_id=message.id,
                                 user_username=check.chat_username, bot_username=username, content=message.text, date=time))
            session.commit()
            print("Added")
        else:
            if message.reply_to_message:
                if message.reply_to_message.from_user.id == (await client.get_me()).id:
                    session.add(Messages(chat_type=check.type, chat_name=message.chat.username, message_id=message.id,
                                         user_username=check.chat_username, bot_username=username, content=message.text,
                                         date=time))
                    session.commit()
                    print("added")


app.run()