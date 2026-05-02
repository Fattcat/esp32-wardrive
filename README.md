- For educational purposes only !

# 🛰️ ESP32-S3 Wardriving System (GPS-RSSI Fusion)

Tento projekt slúži na precízny zber Wi-Fi dát (SSID, BSSID, RSSI) a ich následné priradenie k reálnym budovám pomocou GPS súradníc z modulu NEO-6M. Systém je navrhnutý pre výskumné účely v oblasti kybernetickej bezpečnosti (vulnerability research)

## 🚀 Hlavné funkcie
* **High-Density Logging:** Zaznamenáva každú vzorku (beacon) pre neskoršie štatistické spracovanie.
* **RGB Status UI:** Vizuálna diagnostika v reálnom čase pomocou vstavanej LED na ESP32-S3.
* **Smart Filtering:** Logovanie prebieha len pri dostatočnej presnosti GPS (HDOP filter).
* **Vážený Centroid:** Algoritmus v Pythone eliminuje chyby spôsobené útlmom stien a latenciou GPS.

---

## 🚦 RGB Signalizácia (GPIO 48)

| Farba | Režim | Význam |
| :--- | :--- | :--- |
| **⚪ Biela** | Statická | Inicializácia systému a periférií. |
| **🔴 Červená** | Blikanie | **Chyba SD karty!** Skontrolujte zapojenie alebo formát (FAT32). |
| **🔵 Modrá** | Statická | Vyhľadávanie GPS fixu (Cold Start). Vyjdite na voľné priestranstvo. |
| **🟡 Žltá** | Statická | Nízka presnosť (HDOP > 2.5). Čakanie na lepší signál. |
| **🟢 Zelená** | Statická | **Aktívne logovanie.** Systém pracuje správne. |
| **⚪ Biela** | Záblesk | Potvrdenie úspešného zápisu dát na SD kartu. |

---

## 🛠️ Hardvérové zapojenie (ESP32-S3)
| Komponent | Pin na ESP32-S3 | Poznámka |
| :--- | :--- | :--- |
| **NEO-6M TX** | GPIO 16 (RX2) | Komunikácia 9600 baud |
| **NEO-6M RX** | GPIO 17 (TX2) | |
| **SD CS** | GPIO 5 | SPI zbernica |
| **RGB LED** | GPIO 48 | Interná NeoPixel LED |

---

## 📊 Spracovanie dát (Workflow)

### 1. Zber (ESP32)
Zariadenie počas pohybu vytvára súbor `wardrive.csv`. Neukladá len najsilnejší signál, ale celú trasu ("trace"), čo je kľúčové pre potlačenie multipath efektov (odrazov signálu).

### 2. Analýza (Python)
Používa sa **Vážený centroidný model**. Každé meranie dostáva váhu $W$ na základe RSSI:
$$W = (RSSI + 100)^4$$
Tento vzorec agresívne uprednostňuje silné merania (blízko okien/stien) pred slabými odrazmi, čím lokalizuje router hlbšie v pôdoryse budovy.

### 3. Vizualizácia
Skript automaticky sťahuje polygóny budov z **OpenStreetMap** a priraďuje vypočítané súradnice k najbližším adresným bodom.

---

## 💻 Inštalácia
1. **Arduino IDE:**
   * Nainštaluj knižnice: `TinyGPS++`, `Freenove_WS2812_Lib_for_ESP32`.
   * Doska: `ESP32S3 Dev Module`.
2. **Python:**
   ```bash
   pip install pandas numpy folium osmnx shapely
