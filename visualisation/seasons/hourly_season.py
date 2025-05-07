import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('chat_data.db')
df = pd.read_sql_query("SELECT id, src, dst, timestamp FROM shipments", conn, parse_dates=['timestamp'])
df['month']   = df['timestamp'].dt.to_period('M').astype(str)
df['weekday'] = df['timestamp'].dt.day_name()
df['hour']    = df['timestamp'].dt.hour
df['quarter'] = df['timestamp'].dt.to_period('Q').astype(str)

hourly_counts = df.groupby('hour').size()

plt.figure()
plt.bar(hourly_counts.index, hourly_counts.values)
plt.title('Shipments by Hour of Day')
plt.xlabel('Hour')
plt.ylabel('Number of Shipments')
plt.tight_layout()
plt.show()