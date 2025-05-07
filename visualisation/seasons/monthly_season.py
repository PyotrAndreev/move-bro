import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('chat_data.db')
df = pd.read_sql_query("SELECT id, src, dst, timestamp FROM shipments", conn, parse_dates=['timestamp'])
df['month']   = df['timestamp'].dt.to_period('M').astype(str)
df['weekday'] = df['timestamp'].dt.day_name()
df['hour']    = df['timestamp'].dt.hour
df['quarter'] = df['timestamp'].dt.to_period('Q').astype(str)

monthly_counts = df.groupby('month').size()

plt.figure()
plt.plot(monthly_counts.index, monthly_counts.values, marker='o')
plt.title('Shipments per Month')
plt.xlabel('Month')
plt.ylabel('Number of Shipments')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()