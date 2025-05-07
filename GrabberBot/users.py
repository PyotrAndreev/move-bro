import sqlite3
from pyrogram import Client
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, UsernameNotOccupied, ChatAdminRequired

# ==== Настройки Pyrogram ====
API_ID = 9093213      # ваш API_ID
API_HASH = "7a586baf41613d2d93da8333d3446832"
SESSION_NAME = "my_session"  # имя сессии (например, "bot" или "user")

# ==== Путь к базе ====
DB_PATH = "chat_data.db"


def ensure_users_table(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        sender_id    INTEGER PRIMARY KEY,
        name         TEXT,
        username     TEXT,
        bio          TEXT,
        group_count  INTEGER
    );
    """)


def remove_invalid_users(conn, cur):
    # Удаляем записи без username
    cur.execute("""
        DELETE FROM users
        WHERE username IS NULL
           OR username = '';
    """)
    conn.commit()
    # Выполняем VACUUM вне транзакции
    conn.execute("VACUUM;")
    print("[CLEANUP] Удалены некорректные пользователи и выполнен VACUUM.")


def get_all_senders(cur):
    cur.execute("SELECT DISTINCT sender_id FROM chat_messages;")
    return [row[0] for row in cur.fetchall()]


def get_all_group_links(cur):
    cur.execute("SELECT DISTINCT link FROM chat_links;")
    return [row[0] for row in cur.fetchall()]


def user_exists(cur, user_id):
    cur.execute("SELECT 1 FROM users WHERE sender_id = ?;", (user_id,))
    return cur.fetchone() is not None


def insert_user(cur, user_id, name, username, bio, group_count):
    cur.execute(
        """
        INSERT INTO users (sender_id, name, username, bio, group_count)
        VALUES (?, ?, ?, ?, ?);
        """, (user_id, name, username, bio, group_count)
    )


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    ensure_users_table(cur)
    # Удаляем некорректные записи перед обработкой
    # remove_invalid_users(conn, cur)

    senders = get_all_senders(cur)
    group_links = get_all_group_links(cur)

    with Client(SESSION_NAME, API_ID, API_HASH) as app:
        for user_id in senders:
            if user_exists(cur, user_id):
                continue
            try:
                user = app.get_users(user_id)
            except (PeerIdInvalid, UsernameNotOccupied):
                print(f"[SKIP] Некорректный или несуществующий user_id: {user_id}")
                continue
            except Exception as e:
                print(f"[ERROR] Ошибка при получении {user_id}: {e}")
                continue

            # Формируем поля
            name = "".join(filter(None, [user.first_name, user.last_name]))
            username = user.username
            # bio = user.bio or None
            bio = getattr(user, 'bio', None)

            # Считаем группы
            count = 0
            for link in group_links:
                try:
                    chat = app.get_chat(link)
                    app.get_chat_member(chat.id, user_id)
                    count += 1
                except UserNotParticipant:
                    pass
                except ChatAdminRequired:
                    # Нету прав администратора для проверки участников
                    print(f"[WARN] Нужны права администратора в {link} для проверки {user_id}")
                except (PeerIdInvalid, ValueError):
                    continue
                except Exception as e:
                    print(f"[WARN] Ошибка проверки {link} для {user_id}: {e}")

            insert_user(cur, user_id, name, username, bio, count)
            conn.commit()
            display_name = username and f"@{username}" or name or str(user_id)
            print(f"[ADDED] {user_id} → {display_name}, groups: {count}")

    conn.close()
    print("Готово.")


if __name__ == "__main__":
    main()
