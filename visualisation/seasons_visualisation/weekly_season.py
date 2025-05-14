import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('chat_data.db')
df = pd.read_sql_query(
    "SELECT id, src, dst, timestamp FROM shipments", 
    conn, parse_dates=['timestamp']
)

total_records = len(df)

df['weekday'] = df['timestamp'].dt.day_name()

order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

weekly_counts = df.groupby('weekday').size().reindex(order)

plt.figure()
plt.bar(weekly_counts.index, weekly_counts.values)
plt.title(f'Shipments by Weekday\nTotal records analyzed: {total_records}')
plt.xlabel('Weekday')
plt.ylabel('Number of Shipments')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
