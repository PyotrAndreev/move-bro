import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('chat_data.db')
df = pd.read_sql_query(
    "SELECT id, src, dst, timestamp FROM shipments", 
    conn, parse_dates=['timestamp']
)

total_records = len(df)

df['quarter'] = df['timestamp'].dt.to_period('Q').astype(str)

quarterly_counts = df.groupby('quarter').size()

plt.figure()
plt.plot(quarterly_counts.index, quarterly_counts.values, marker='o')
plt.title(f'Quarterly Shipment Counts\nTotal records analyzed: {total_records}')
plt.xlabel('Quarter')
plt.ylabel('Number of Shipments')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
