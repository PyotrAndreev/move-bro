import sqlite3
import pandas as pd
from geopy.geocoders import Nominatim
import folium


def is_valid_place(place):
    return isinstance(place, str) and place.strip() != ''

conn = sqlite3.connect('chat_data.db')
df = pd.read_sql_query('SELECT src, dst FROM shipments', conn)

mask = df['src'].apply(is_valid_place) & df['dst'].apply(is_valid_place)
df = df[mask].reset_index(drop=True)


geoloc = Nominatim(user_agent="shipments_simple")
def geocode_safe(name):
    try:
        loc = geoloc.geocode(name, timeout=10)
        if loc:
            return loc.latitude, loc.longitude
    except Exception:
        pass
    return None, None


places = pd.Series(pd.concat([df.src, df.dst]).unique(), name='place')
coords = {p: geocode_safe(p) for p in places}
coords_df = pd.DataFrame([
    {'place': p, 'lat': lat, 'lon': lon}
    for p, (lat, lon) in coords.items() if lat is not None
])

src_coords = coords_df.rename(columns={'place': 'src', 'lat': 'src_lat', 'lon': 'src_lon'})
dst_coords = coords_df.rename(columns={'place': 'dst', 'lat': 'dst_lat', 'lon': 'dst_lon'})

df = df.merge(src_coords, on='src').merge(dst_coords, on='dst')

if not df.empty:
    avg_lat = coords_df['lat'].mean()
    avg_lon = coords_df['lon'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5, tiles='CartoDB positron')

    for _, row in coords_df.iterrows():
        if row['place'] in df['src'].values:
            folium.Marker(
                location=(row.lat, row.lon),
                popup=f"Отправка: {row.place}",
                icon=folium.Icon(color='blue', icon='arrow-up')
            ).add_to(m)
        if row['place'] in df['dst'].values:
            folium.Marker(
                location=(row.lat, row.lon),
                popup=f"Получение: {row.place}",
                icon=folium.Icon(color='green', icon='arrow-down')
            ).add_to(m)

    for _, r in df.iterrows():
        folium.PolyLine(
            locations=[(r.src_lat, r.src_lon), (r.dst_lat, r.dst_lon)],
            weight=2,
            color='gray'
        ).add_to(m)

    m.save('shipments_map.html')
    print("Карта сохранена: shipments_map.html")
else:
    print("Нет данных для визуализации.")
