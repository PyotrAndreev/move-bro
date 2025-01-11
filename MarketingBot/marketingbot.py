from pyrogram import Client, filters
from pytz import timezone
from dotenv import load_dotenv
import os
from control import Do

load_dotenv("bots/.env.bot1")
do = Do()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
admin_id = int(os.getenv("ADMIN_ID"))
username = os.getenv("BOT_USERNAME")
app = Client(username, api_id=api_id, api_hash=api_hash)


@app.on_message(filters.command("start"))
def start_command(client, message):
    message.reply_text(f"Бот работает. Твой userid: {message.from_user.id}")

async def send_messages(client, message, id):
    chats = do.getChats(bot_username=username)
    text = do.getTemplates(id=int(id))
    if (not text):
        await message.reply_text("Нет такого шаблона")
    else:
        text = text.content
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
                do.addMessage(chat_type=chat_type, chat_name=message.chat.username, message_id=message.id, user_username=chat_id, bot_username=username, content=id, date=time, is_template=True)
                print(f"Сообщение отправлено {chat_id}")
                print(f"В базе {len(do.getMessages())} сообщений")
            except Exception as e:
                print(f"Ошибка при отправке сообщения {chat_id}: {e}")
        await message.reply("Сообщения отправлены всем пользователям.")

@app.on_message(filters.command("send_all") & filters.user(admin_id))
async def command_send_all(client, message):
    id = message.text.markdown[len("/send_all "):].strip()
    print(id)
    if (id.isdigit()):
        await send_messages(client, message, id)

@app.on_message(filters.command("add") & filters.user(admin_id))
async def add_user(client, message):
    user = message.text.markdown[len("/add "):].strip().lower()
    if (user[0] != '@'):
        await message.reply(f'Формат: @user')
    else:
        print(user[1:])
        try:
            chat_type = await app.get_chat(user[1:])
            check = do.getChats(chat_username=user[1:], first=True)
            if (str(chat_type.type)[9:] == "PRIVATE" and not check):
                do.addChat(atype='dm', chat_username=user[1:], chat_id=chat_type.id, bot_username=username)
                if (not do.getUsers(username=user[1:])):
                    do.addUser(username = user[1:], tg_id=chat_type.id, name=chat_type.first_name, lastname=str(chat_type.last_name), bot_username=username)
                # print(user[1:], chat_type.id, chat_type.first_name, chat_type.last_name)
                await message.reply(f'{user} добавлен')
            elif (str(chat_type.type)[9:] == "SUPERGROUP" and not check):
                do.addChat(atype='group', chat_username=user[1:], chat_id=chat_type.id, bot_username=username)
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
            check = do.getChats(chat_username=user[1:], first=True)
            if (check):
                do.delete(check)
                print(len(do.getChats()))
                await message.reply(f'{user} удален из базы')
            else:
                await message.reply('Чата нет в базе')
        except Exception as e:
            await message.reply(f"Неверный юзернейм. {str(e)}")

@app.on_message(filters.command("show") & filters.user(admin_id))
async def show_all(client, message):
    names = [f'@{i.chat_username} - type: {i.type}' for i in do.getChats()]
    if names:
        await message.reply('\n'.join(names))
    print('\n'.join(names))

@app.on_message(filters.command("temp") & filters.user(admin_id))
async def templates(client, message):
    tmps = [f'{i.id}: {i.content}' for i in do.getTemplates()]
    await message.reply('\n'.join(tmps))
    print('\n'.join(tmps))


@app.on_message()
async def other(client, message):
    proceed = True
    if (message.from_user.username == username):
        proceed = False
    time = message.date.astimezone(timezone("Europe/Moscow"))
    check = do.getChats(chat_username=str(message.chat.username), first=True)
    if (proceed and check and message.text != None and message.chat.username):
        if check.type == 'dm':
            print(message.chat)
            do.addMessage(chat_type=check.type, chat_name=message.chat.username, message_id=message.id, user_username=check.chat_username, bot_username=username, content=message.text, date=time)
            print("Added")
        else:
            if message.reply_to_message:
                if message.reply_to_message.from_user.id == (await client.get_me()).id:
                    do.addMessage(chat_type=check.type, chat_name=message.chat.username, message_id=message.id,user_username=check.chat_username, bot_username=username, content=message.text, date=time)
                    print("added")

app.run()