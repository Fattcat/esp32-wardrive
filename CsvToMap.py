import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap

def analyze_wardrive(file_path):
    df = pd.read_csv(file_path)
    
    # Odstránenie extrémnych nepresností
    df = df[(df['hdop'] < 2.0) & (df['rssi'] > -85)]

    def calculate_smart_centroid(group):
        if len(group) < 3: return None # Ignorujeme náhodné zachytenia
        
        # Odstránenie outlierov v polohe (napr. ak GPS "skočilo")
        q1_lat, q3_lat = group['lat'].quantile([0.25, 0.75])
        q1_lon, q3_lon = group['lon'].quantile([0.25, 0.75])
        iqr_lat = q3_lat - q1_lat
        iqr_lon = q3_lon - q1_lon
        
        filtered = group[
            (group['lat'] >= q1_lat - 1.5*iqr_lat) & (group['lat'] <= q3_lat + 1.5*iqr_lat) &
            (group['lon'] >= q1_lon - 1.5*iqr_lon) & (group['lon'] <= q3_lon + 1.5*iqr_lon)
        ]

        if filtered.empty: filtered = group

        # Váha: Exponenciálne RSSI
        # Normalizujeme RSSI (napr. -30 je silné, -85 slabé)
        weights = np.exp((filtered['rssi'] + 90) / 10)
        
        return pd.Series({
            'lat': np.sum(filtered['lat'] * weights) / np.sum(weights),
            'lon': np.sum(filtered['lon'] * weights) / np.sum(weights),
            'max_rssi': filtered['rssi'].max(),
            'count': len(filtered)
        })

    # Spracovanie
    results = df.groupby('bssid').apply(calculate_smart_centroid).dropna().reset_index()

    # Tvorba mapy
    m = folium.Map(location=[results['lat'].mean(), results['lon'].mean()], zoom_start=16)
    
    # Vrstva 1: Body routerov
    for _, row in results.iterrows():
        color = 'green' if row['max_rssi'] > -60 else 'blue' if row['max_rssi'] > -75 else 'red'
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=6,
            popup=f"BSSID: {row['bssid']}<br>RSSI: {row['max_rssi']}dBm",
            color=color,
            fill=True
        ).add_to(m)

    # Vrstva 2: HeatMap (hustota sietí)
    heat_data = [[row['lat'], row['lon']] for _, row in results.iterrows()]
    HeatMap(heat_data, name="Hustota sietí").add_to(m)

    folium.LayerControl().add_to(m)
    m.save('wardrive_vylepseny.html')
    print("Analýza hotová. Otvorte wardrive_vylepseny.html")

if __name__ == "__main__":
    analyze_wardrive('wardrive.csv')
