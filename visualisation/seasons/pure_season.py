import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('chat_data.db')
df = pd.read_sql_query("SELECT id, src, dst, timestamp FROM shipments", conn, parse_dates=['timestamp'])
df['month']   = df['timestamp'].dt.to_period('M').astype(str)
df['weekday'] = df['timestamp'].dt.day_name()
df['hour']    = df['timestamp'].dt.hour
df['quarter'] = df['timestamp'].dt.to_period('Q').astype(str)

def month_to_season(month):
    if month in (12, 1, 2):
        return 'Winter'
    elif month in (3, 4, 5):
        return 'Spring'
    elif month in (6, 7, 8):
        return 'Summer'
    else:
        return 'Autumn'

# Добавляем колонку season
df['season'] = df['timestamp'].dt.month.map(month_to_season)

# Агрегируем по сезонам
season_order = ['Winter','Spring','Summer','Autumn']
season_counts = df.groupby('season').size().reindex(season_order)

# Столбчатая диаграмма по сезонам
df['year'] = df['timestamp'].dt.year
season_year = df.groupby(['year','season']).size().unstack().reindex(columns=season_order)

plt.figure()
for season in season_order:
    plt.plot(season_year.index, season_year[season], marker='o', label=season)
plt.title('Seasonal Shipment Trends by Year')
plt.xlabel('Year')
plt.ylabel('Number of Shipments')
plt.legend()
plt.tight_layout()
plt.show()