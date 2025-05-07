import sqlite3
import pandas as pd
from geopy.geocoders import Nominatim
import folium

# Простая функция валидации

def is_valid_place(place):
    return isinstance(place, str) and place.strip() != ''

# Читаем данные
conn = sqlite3.connect('chat_data.db')
df = pd.read_sql_query('SELECT src, dst FROM shipments', conn)
# Фильтрация некорректных записей
mask = df['src'].apply(is_valid_place) & df['dst'].apply(is_valid_place)
df = df[mask].reset_index(drop=True)

# Геокодер
geoloc = Nominatim(user_agent="shipments_simple")
def geocode_safe(name):
    try:
        loc = geoloc.geocode(name, timeout=10)
        if loc:
            return loc.latitude, loc.longitude
    except Exception:
        pass
    return None, None

# Геокодирование
places = pd.Series(pd.concat([df.src, df.dst]).unique(), name='place')
coords = {p: geocode_safe(p) for p in places}
coords_df = pd.DataFrame([
    {'place': p, 'lat': lat, 'lon': lon}
    for p, (lat, lon) in coords.items() if lat is not None
])
# Объединение координат
df = df.merge(coords_df.rename(columns={'place':'src','lat':'src_lat','lon':'src_lon'}), on='src')
df = df.merge(coords_df.rename(columns={'place':'dst','lat':'dst_lat','lon':'dst_lon'}), on='dst')

# Создание карты с минимальными элементами
if not df.empty:
    avg_lat = coords_df['lat'].mean()
    avg_lon = coords_df['lon'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5, tiles='CartoDB positron', control_scale=False)

    # Добавляем простые маркеры
    for _, r in coords_df.iterrows():
        folium.Marker(location=(r.lat, r.lon), popup=r.place).add_to(m)

    # Добавляем простые линии маршрутов
    for _, r in df.iterrows():
        folium.PolyLine(locations=[(r.src_lat, r.src_lon), (r.dst_lat, r.dst_lon)], weight=2).add_to(m)

    m.save('shipments_map.html')
    print("Карта сохранена: shipments_map.html")
else:
    print("Нет данных для визуализации.")
