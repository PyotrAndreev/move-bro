import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('chat_data.db')
df = pd.read_sql_query(
    "SELECT id, src, dst, timestamp FROM shipments", 
    conn, parse_dates=['timestamp']
)

total_records = len(df)

df['hour'] = df['timestamp'].dt.hour

hourly_counts = df.groupby('hour').size()

plt.figure()
plt.bar(hourly_counts.index, hourly_counts.values)
plt.title(f'Shipments by Hour of Day\nTotal records analyzed: {total_records}')
plt.xlabel('Hour')
plt.ylabel('Number of Shipments')

plt.tight_layout()
plt.show()
