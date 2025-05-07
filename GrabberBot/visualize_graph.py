import sqlite3
import pandas as pd
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt

conn = sqlite3.connect('chat_data.db')
df = pd.read_sql_query('SELECT src, dst FROM shipments', conn)

geolocator = Nominatim(user_agent="shipments_country_chart")
_place_to_country = {}  # кэш

def get_country(place_name):
    if place_name in _place_to_country:
        return _place_to_country[place_name]
    try:
        loc = geolocator.geocode(place_name, timeout=10, addressdetails=True)
        country = None
        if loc and 'address' in loc.raw:
            country = loc.raw['address'].get('country')
        _place_to_country[place_name] = country
        return country
    except Exception:
        _place_to_country[place_name] = None
        return None

df['src_country'] = df['src'].apply(get_country)
df['dst_country'] = df['dst'].apply(get_country)

df_send = df[df['src_country'].notna()]
df_recv = df[df['dst_country'].notna()]

send_counts = df_send['src_country'].value_counts()
recv_counts = df_recv['dst_country'].value_counts()

plt.figure(figsize=(10, 6))
send_counts.plot(kind='bar')
plt.title('Количество отправлений по странам')
plt.xlabel('Страна')
plt.ylabel('Число отправлений')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
recv_counts.plot(kind='bar', color='orange')
plt.title('Количество доставок по странам')
plt.xlabel('Страна')
plt.ylabel('Число доставок')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
