import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('chat_data.db')
df = pd.read_sql_query(
    "SELECT id, src, dst, timestamp FROM shipments", 
    conn, parse_dates=['timestamp']
)

total_records = len(df)

df['month']   = df['timestamp'].dt.to_period('M').astype(str)
df['weekday'] = df['timestamp'].dt.day_name()
df['hour']    = df['timestamp'].dt.hour
df['quarter'] = df['timestamp'].dt.to_period('Q').astype(str)

order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

pivot = (
    df
    .pivot_table(index='weekday', columns='hour', values='id', aggfunc='count')
    .reindex(order)
)

plt.figure(figsize=(10, 6))
plt.imshow(pivot, aspect='auto')

plt.title(f'Heatmap of Shipments: Weekday vs Hour\nTotal records analyzed: {total_records}')
plt.xlabel('Hour of Day')
plt.ylabel('Weekday')
plt.yticks(range(len(pivot.index)), pivot.index)
plt.xticks(range(len(pivot.columns)), pivot.columns)

plt.tight_layout()
plt.show()