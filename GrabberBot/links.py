import os
import sqlite3
import asyncio
from pyrogram import Client, errors

# Configuration: set your API credentials as environment variables or fill in directly
API_ID = int(os.getenv("API_ID", "9093213"))
API_HASH = os.getenv("API_HASH", "7a586baf41613d2d93da8333d3446832")

# SQLite database path
DB_PATH = "chat_data.db"
TABLE_NAME = "found_links"

async def main():
    # Initialize Pyrogram client
    app = Client("checker", api_id=API_ID, api_hash=API_HASH)
    await app.start()

    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure there's a column to store results
    try:
        cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN is_open_supergroup INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists
        pass

    # Fetch all links
    cursor.execute(f"SELECT rowid, link FROM {TABLE_NAME}")
    rows = cursor.fetchall()

    for rowid, raw in rows:
        # Normalize link: remove t.me/ prefix or @
        username = raw.strip()
        if username.startswith("t.me/"):
            username = username.split("t.me/")[-1]
        if username.startswith("@"):
            username = username[1:]

        is_open = 0
        try:
            chat = await app.get_chat(username)
            # Check if it's a supergroup and has a public username
            if str(chat.type) == "ChatType.SUPERGROUP" and chat.username:
                is_open = 1
        except errors.RPCError as e:
            print(f"Failed to fetch {username}: {e}")

        # Update result
        cursor.execute(
            f"UPDATE {TABLE_NAME} SET is_open_supergroup = ? WHERE rowid = ?",
            (is_open, rowid)
        )
        conn.commit()
        print(f"{raw} -> {'open supergroup' if is_open else 'not open or error'}")

    # Cleanup
    await app.stop()
    conn.close()

if __name__ == "__main__":
    asyncio.run(main())
