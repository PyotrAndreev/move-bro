import sqlite3
import pandas as pd
from geopy.geocoders import Nominatim
import folium

# Параметры (установите здесь нужные значения):
DB_PATH = 'chat_data.db'           # Путь к файлу SQLite
SRC_COL = 'src'                    # Столбец "откуда"
DST_COL = 'dst'                    # Столбец "куда"
TIME_COL = 'timestamp'             # Столбец с отметкой времени
START_DATE = '2024-12-01'          # Начальная дата (YYYY-MM-DD)
END_DATE = '2025-03-01'            # Конечная дата (YYYY-MM-DD)
GEO_AGENT = 'shipments_simple'     # user_agent для Geopy
# OUTPUT_HTML = f'shipments_map{START_DATE}to{END_DATE}.html' # Имя выходного HTML-файла для карты
OUTPUT_HTML = "2024-2025winter.html"

def load_data(db_path: str, src: str, dst: str, time_col: str, start: str, end: str) -> pd.DataFrame:
    """
    Загрузить данные из таблицы shipments за указанный период.
    """
    conn = sqlite3.connect(db_path)
    query = (
        f"SELECT {src} AS src, {dst} AS dst, {time_col} AS ts "
        f"FROM shipments "
        f"WHERE date({time_col}) BETWEEN date('{start}') AND date('{end}')"
    )
    df = pd.read_sql_query(query, conn, parse_dates=['ts'])
    conn.close()
    df.rename(columns={'ts': time_col}, inplace=True)
    return df


def geocode_safe(name: str, geoloc: Nominatim) -> tuple:
    """
    Безопасное геокодирование через Nominatim.
    """
    try:
        loc = geoloc.geocode(name, timeout=10)
        if loc:
            return loc.latitude, loc.longitude
    except Exception:
        pass
    return None, None


def create_map(df: pd.DataFrame, src: str, dst: str, geoloc_agent: str, output_html: str):
    """
    Построить и сохранить интерактивную карту маршрутов в HTML.
    """
    # Фильтруем валидные строки: непустые строки в src и dst
    mask_src = df[src].apply(lambda x: isinstance(x, str) and x.strip() != '')
    mask_dst = df[dst].apply(lambda x: isinstance(x, str) and x.strip() != '')
    df = df[mask_src & mask_dst]

    if df.empty:
        print("Нет данных для визуализации.")
        return

    # Геокодирование уникальных мест
    geoloc = Nominatim(user_agent=geoloc_agent)
    unique_places = pd.Series(pd.concat([df[src], df[dst]]).unique(), name='place')
    coords = {place: geocode_safe(place, geoloc) for place in unique_places}
    coords_df = pd.DataFrame([
        {'place': p, 'lat': lat, 'lon': lon}
        for p, (lat, lon) in coords.items() if lat is not None
    ])

    # Слияние координат по src и dst
    src_coords = coords_df.rename(columns={'place': src, 'lat': 'src_lat', 'lon': 'src_lon'})
    dst_coords = coords_df.rename(columns={'place': dst, 'lat': 'dst_lat', 'lon': 'dst_lon'})
    df = df.merge(src_coords, on=src).merge(dst_coords, on=dst)

    # Инициализация карты
    avg_lat = coords_df['lat'].mean()
    avg_lon = coords_df['lon'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5, tiles='CartoDB positron')

    # Добавляем маркеры: отправка и получение
    for _, row in coords_df.iterrows():
        place = row['place']
        lat, lon = row['lat'], row['lon']
        if place in df[src].values:
            folium.Marker(
                (lat, lon), popup=f"Отправка: {place}",
                icon=folium.Icon(color='blue', icon='arrow-up')
            ).add_to(m)
        if place in df[dst].values:
            folium.Marker(
                (lat, lon), popup=f"Получение: {place}",
                icon=folium.Icon(color='green', icon='arrow-down')
            ).add_to(m)

    # Добавляем линии маршрутов
    for _, r in df.iterrows():
        folium.PolyLine(
            locations=[(r['src_lat'], r['src_lon']), (r['dst_lat'], r['dst_lon'])],
            weight=2, color='gray'
        ).add_to(m)

    # Сохраняем карту
    m.save(output_html)
    print(f"Карта сохранена: {output_html}")


def main():
    # Загрузка данных и визуализация
    df = load_data(DB_PATH, SRC_COL, DST_COL, TIME_COL, START_DATE, END_DATE)
    create_map(df, SRC_COL, DST_COL, GEO_AGENT, OUTPUT_HTML)


if __name__ == '__main__':
    main()
