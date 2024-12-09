from database import get_db, Chats, Messages, Users, Templates, Logs, Bots
from pytz import timezone
from datetime import datetime

class Do:
    def __init__(self):
        self.session = next(get_db())

    def compare(self, variable, typeof):
        if (type(variable) != typeof):
            raise TypeError

    def time(self):
        return datetime.now(timezone("Europe/Moscow"))

    def addMessage(self, chat_type, chat_name, message_id, user_username, bot_username, content, date, is_template=False):
        try:
            self.compare(chat_type, str)
            self.compare(chat_name, str)
            self.compare(message_id, int)
            self.compare(is_template, bool)
            self.compare(user_username, str)
            self.compare(bot_username, str)
            self.compare(content, str)
        except TypeError:
            self.addLog(action="problem while adding message", date=self.time(), bot_username=bot_username)
            print("Неверные данные1")
            return False

        try:
            self.session.add(Messages(chat_type=chat_type, chat_name=chat_name, message_id=message_id, user_username=user_username, bot_username=bot_username, content=content, date=date, is_template=is_template))
            self.session.commit()
            self.addLog(action="message added", date=self.time(), bot_username=bot_username)
        except Exception as e:
            self.addLog(action="problem while adding message", date=self.time(), bot_username=bot_username)
            print(f"Ошибка: {e}")

    def adduser(self, username, tg_id, name, bot_username, lastname=''):
        try:
            self.compare(username, str)
            self.compare(tg_id, int)
            self.compare(name, str)
            self.compare(lastname, str)
            self.compare(bot_username, str)
        except TypeError:
            self.addLog(action="problem while adding user", date=self.time(), bot_username=bot_username)
            print("Неверные данные2")
            return False

        try:
            self.session.add(Users(username=username, tg_id=tg_id, name=name, lastname=lastname))
            self.session.commit()
            self.addLog(action="user added", date=self.time(), bot_username=bot_username)
        except Exception as e:
            self.addLog(action="problem while adding user", date=self.time(), bot_username=bot_username)
            print(f"Ошибка: {e}")

    def addBot(self, username, tg_id, admin_id):
        try:
            self.compare(username, str)
            self.compare(tg_id, int)
            self.compare(admin_id, int)
        except TypeError:
            self.addLog(action="problem while adding bot", date=self.time(), bot_username=username)
            print("Неверные данные3")
            return False

        try:
            self.session.add(Bots(username=username, tg_id=tg_id, admin_id=admin_id))
            self.session.commit()
            self.addLog(action="bot added", date=self.time(), bot_username=username)
        except Exception as e:
            self.addLog(action="problem while adding bot", date=self.time(), bot_username=username)
            print(f"Ошибка: {e}")

    def addLog(self, action, date, bot_username):
        try:
            self.compare(action, str)
            self.compare(bot_username, str)
        except TypeError:
            print("Неверные данные4")
            return False

        try:
            self.session.add(Logs(action=action, date=date, bot_username=bot_username))
            self.session.commit()
        except Exception as e:
            print(f"Ошибка: {e}")

    def addTemplate(self, content):
        try:
            self.compare(content, str)
        except TypeError:
            print("Неверные данные5")
            return False

        try:
            self.session.add(Templates(content=content))
            self.session.commit()
        except Exception as e:
            print(f"Ошибка: {e}")

    def addChat(self, atype, chat_username, chat_id, bot_username):
        try:
            self.compare(atype, str)
            self.compare(chat_username, str)
            self.compare(chat_id, int)
            self.compare(bot_username, str)
        except TypeError:
            self.addLog(action="problem while adding chat", date=self.time(), bot_username=bot_username)
            print("Неверные данные6")
            return False

        try:
            self.session.add(Chats(type=atype, chat_username=chat_username, chat_id=chat_id, bot_username=bot_username))
            self.session.commit()
            self.addLog(action="chat added", date=self.time(), bot_username=bot_username)
        except Exception as e:
            self.addLog(action="problem while adding chat", date=self.time(), bot_username=bot_username)
            print(f"Ошибка: {e}")

    def getChats(self, atype='', chat_username='', chat_id = 0, tg_bot_id=0, bot_username='', first=False):
        try:
            self.compare(atype, str)
            self.compare(chat_username, str)
            self.compare(chat_id, int)
            self.compare(bot_username, str)
            self.compare(first, bool)
        except TypeError:
            print("Неверные данные7")
            return False

        try:
            chats = self.session.query(Chats)
        except Exception as e:
            print(e)
            return False
        if atype:
            chats = chats.filter(Chats.type==atype)
        if chat_username:
            chats = chats.filter(Chats.chat_username==chat_username)
        if chat_id:
            chats = chats.filter(Chats.chat_id==chat_id)
        if tg_bot_id:
            chats = chats.filter(Chats.tg_bot_id==tg_bot_id)
        if bot_username:
            chats = chats.filter(Chats.bot_username == bot_username)
        if first:
            return chats.first()
        return chats.all()
    
    def getUsers(self, username='', tg_id=0, name='', lastname='', first=False):
        try:
            self.compare(username, str)
            self.compare(tg_id, int)
            self.compare(name, str)
            self.compare(lastname, str)
            self.compare(first, bool)
        except TypeError:
            print("Неверные данные8")
            return False

        try:
            users = self.session.query(Users)
        except Exception:
            return False
        if username:
            users = users.filter(Users.username == username)
        if tg_id:
            users = users.filter(Users.tg_id==tg_id)
        if name:
            users = users.filter(Users.name==name)
        if lastname:
            users = users.filter(Users.lastname==lastname)
        if first:
            return users.first()
        return users.all()
    
    def getMessages(self, chat_type='', is_template = False, chat_name='', message_id=0, user_username='', bot_username='', content='', date='', first=False):
        try:
            self.compare(chat_type, str)
            self.compare(chat_name, str)
            self.compare(message_id, int)
            self.compare(is_template, bool)
            self.compare(user_username, str)
            self.compare(bot_username, str)
            self.compare(content, str)
        except TypeError:
            print("Неверные данные9")
            return False

        try:
            messages = self.session.query(Messages)
        except Exception:
            return False
        if chat_type:
            messages = messages.filter(Messages.chat_type==chat_type)
        if chat_name:
            messages = messages.filter(Messages.chat_name==chat_name)
        if message_id:
            messages = messages.filter(Messages.message_id==message_id)
        if user_username:
            messages = messages.filter(Messages.user_username==user_username)
        if bot_username:
            messages = messages.filter(Messages.bot_username==bot_username)
        if content:
            messages = messages.filter(Messages.content==content)
        if date:
            messages = messages.filter(Messages.date==date)
        if first:
            return messages.first()
        return messages.all()
    
    def getTemplates(self, id=0):
        try:
            self.compare(id, int)
        except TypeError:
            print("Неверные данные0")
            return False
        try:
            templates = self.session.query(Templates)
        except Exception:
            return False
        if id:
            templates = templates.filter(Templates.id==id)
            return templates.first()
        return templates.all()
    
    def getBots(self, username='', tg_id=0, admin_id=0, first=False):
        try:
            self.compare(username, str)
            self.compare(tg_id, int)
            self.compare(admin_id, int)
            self.compare(first, bool)
        except TypeError:
            print("Неверные данные11")
            return False

        try:
            bots = self.session.query(Bots)
        except Exception:
            return False
        if username:
            bots = bots.filter(Bots.username==username)
        if tg_id:
            bots = bots.filter(Bots.tg_id==tg_id)
        if admin_id:
            bots = bots.filter(Bots.admin_id==admin_id)
        if first:
            return bots.first()
        return bots.all()
    
    def getLogs(self, action='', date='', bot_username='', first=False):
        try:
            self.compare(action, str)
            self.compare(bot_username, str)
            self.compare(first, bool)
        except TypeError:
            print("Неверные данные12")
            return False

        try:
            logs = self.session.query(Logs)
        except Exception:
            return False
        if action:
            logs = logs.filter(Logs.action==action)
        if date:
            logs = logs.filter(Logs.date==date)
        if bot_username:
            logs = logs.filter(Logs.bot_username==bot_username)
        if first:
            return logs.first()
        return logs.all()

    def delete(self, item):
        try:
            self.session.delete(item)
            self.session.commit()
        except Exception as e:
            print(f"Ошибка: {e}")