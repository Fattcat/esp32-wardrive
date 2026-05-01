import pandas as pd
import numpy as np
import folium
import osmnx as ox
from shapely.geometry import Point

def generate_wardrive_map(input_csv):
    # 1. Načítanie a základné spracovanie
    df = pd.read_csv(input_csv)
    df = df[(df['rssi'] > -85) & (df['hdop'] < 2.5)]

    # Výpočet váženého centroidu (predošlá logika)
    def get_centroid(group):
        weights = np.power(group['rssi'] + 100, 4)
        return pd.Series({
            'lat': np.sum(group['lat'] * weights) / np.sum(weights),
            'lon': np.sum(group['lon'] * weights) / np.sum(weights),
            'max_rssi': group['rssi'].max()
        })

    routers = df.groupby('bssid').apply(get_centroid).reset_index()

    # 2. Získanie budov z OpenStreetMap (OSM)
    # Stiahneme budovy v okolí priemerného bodu tvojej trasy (napr. rádius 1km)
    avg_lat, avg_lon = routers['lat'].mean(), routers['lon'].mean()
    print("Sťahujem mapové podklady z OpenStreetMap...")
    buildings = ox.features_from_point((avg_lat, avg_lon), tags={'building': True}, dist=1000)

    # 3. Vytvorenie mapy
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=17, tiles='cartodbpositron')

    # Pridanie vrstvy budov do HTML mapy pre vizuálnu kontrolu
    folium.GeoJson(buildings.to_json(), name="Budovy (OSM)", 
                   style_function=lambda x: {'fillColor': 'gray', 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.2}
                  ).add_to(m)

    # 4. Priradenie routerov a ich zobrazenie
    for _, row in routers.iterrows():
        point = Point(row['lon'], row['lat'])
        
        # Nájdenie najbližšej budovy a jej adresy (ak existuje v OSM)
        # Toto priradí súradnicu priamo k objektu budovy
        distances = buildings.distance(point)
        nearest_idx = distances.idxmin()
        building_info = buildings.loc[nearest_idx]
        
        addr = building_info.get('addr:street', 'Neznáma ulica')
        num = building_info.get('addr:housenumber', '?')

        # Výber farby podľa sily signálu
        color = 'green' if row['max_rssi'] > -65 else 'orange' if row['max_rssi'] > -80 else 'red'

        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f"<b>BSSID:</b> {row['bssid']}<br><b>RSSI:</b> {row['max_rssi']} dBm<br><b>Budova:</b> {addr} {num}",
            icon=folium.Icon(color=color, icon='wifi', prefix='fa')
        ).add_to(m)

    m.save('wardrive_results.html')
    print("Mapa hotová! Otvor 'wardrive_results.html'.")

# Spusti s tvojím súborom
generate_wardrive_map('wardrive.csv')
