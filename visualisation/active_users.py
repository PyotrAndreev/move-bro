import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Bot
import time

DB_PATH = 'chat_data.db'
BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TOP_N = 10
SLEEP_BETWEEN_REQUESTS = 0.3

conn = sqlite3.connect(DB_PATH)
msgs = pd.read_sql_query("SELECT sender_id FROM chat_messages", conn)
conn.close()

top_senders = msgs['sender_id'].value_counts().head(TOP_N)

bot = Bot(token=BOT_TOKEN)
id_to_username = {}

for uid in top_senders.index:
    try:
        user = bot.get_chat(uid)
        if user.username:
            username = f"@{user.username}"
        elif user.first_name:
            username = user.first_name
        else:
            username = str(uid)
    except Exception as e:
        username = str(uid)
    id_to_username[uid] = username
    time.sleep(SLEEP_BETWEEN_REQUESTS)

usernames = [id_to_username[uid] for uid in top_senders.index]
message_counts = top_senders.values

plt.figure(figsize=(10, 6))
plt.bar(usernames, message_counts)
plt.title(f'Top {TOP_N} Active Users by Username')
plt.xlabel('Username')
plt.ylabel('Number of Messages')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()