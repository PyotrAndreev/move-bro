import sqlite3
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from folium.plugins import AntPath

# --- Функция для валидации входных данных ---
def is_valid_place(place):
    # Допустим, корректное значение — непустая строка
    return isinstance(place, str) and place.strip() != ''

# 1. Читаем таблицу shipments из базы SQLite
conn = sqlite3.connect('chat_data.db')
df = pd.read_sql_query('SELECT src, dst FROM shipments', conn)

# 2. Фильтруем некорректные записи сразу
mask_valid = df['src'].apply(is_valid_place) & df['dst'].apply(is_valid_place)
df = df[mask_valid].reset_index(drop=True)

# 3. Геокодер
geoloc = Nominatim(user_agent="shipments_viz")
def geocode_safe(name):
    try:
        loc = geoloc.geocode(name, timeout=10)
        if loc:
            return loc.latitude, loc.longitude
    except Exception:
        pass
    return None, None

# 4. Геокодирование уникальных мест
places = pd.Series(pd.concat([df.src, df.dst]).unique(), name='place')
coords = {}
for place in places:
    coords[place] = geocode_safe(place)

# 5. Добавляем столбцы координат
coords_df = pd.DataFrame([
    {'place': p, 'lat': coords[p][0], 'lon': coords[p][1]}
    for p in coords if coords[p][0] is not None
])
df = df.merge(coords_df.rename(columns={'place':'src','lat':'src_lat','lon':'src_lon'}), on='src', how='inner')

df = df.merge(coords_df.rename(columns={'place':'dst','lat':'dst_lat','lon':'dst_lon'}), on='dst', how='inner')

# 6. Создание карты
if not df.empty:
    center = [coords_df.lat.mean(), coords_df.lon.mean()]
    m = folium.Map(location=center, zoom_start=4)

    # Маркеры
    for _, row in coords_df.iterrows():
        folium.CircleMarker(
            location=(row.lat, row.lon),
            radius=5,
            popup=row.place
        ).add_to(m)

    # Маршруты
    for _, row in df.iterrows():
        AntPath(
            locations=[(row.src_lat, row.src_lon), (row.dst_lat, row.dst_lon)],
            dash_array=[10, 20], delay=1000
        ).add_to(m)

    # Сохранение
    m.save('shipments_map.html')
    print("Карта успешно сохранена в shipments_map.html")
else:
    print("Нет корректных данных для визуализации.")