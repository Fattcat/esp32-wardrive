#include <WiFi.h>
#include <TinyGPS++.h>
#include <FS.h>
#include <SD.h>
#include <Freenove_WS2812_Lib_for_ESP32.h>

// --- HW Konfigurácia ---
#define LED_PIN   48  
#define SD_CS     5   
#define GPS_RX    16  
#define GPS_TX    17  

TinyGPSPlus gps;
Freenove_ESP32_WS2812 led(1, LED_PIN, 0, TYPE_GRB);
bool sdAvailable = false;

void setLED(uint8_t r, uint8_t g, uint8_t b) {
  led.setLedColorData(0, r, g, b);
  led.show();
}

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
  led.begin();
  led.setBrightness(20);

  setLED(255, 255, 255); // Inicializácia

  if (!SD.begin(SD_CS)) {
    Serial.println("SD Fail");
    while(1) { setLED(255, 0, 0); delay(200); setLED(0, 0, 0); delay(200); }
  }
  sdAvailable = true;

  File f = SD.open("/wardrive.csv", FILE_APPEND);
  if (f && f.size() == 0) f.println("bssid,rssi,lat,lon,hdop,alt,speed");
  f.close();
}

void loop() {
  while (Serial2.available() > 0) gps.encode(Serial2.read());

  // Stavová logika
  if (!gps.location.isValid()) {
    setLED(0, 0, 255); // Modrá - hľadám GPS
  } else if (gps.hdop.hdop() > 2.0) {
    setLED(255, 100, 0); // Oranžová - nízka presnosť
  } else {
    setLED(0, 255, 0); // Zelená - Ready
    
    // Asynchrónny sken (neblokuje GPS)
    int n = WiFi.scanNetworks(false, false, false, 150); 
    
    if (n > 0) {
      File logFile = SD.open("/wardrive.csv", FILE_APPEND);
      if (logFile) {
        for (int i = 0; i < n; ++i) {
          logFile.printf("%s,%d,%.6f,%.6f,%.2f,%.1f,%.2f\n", 
            WiFi.BSSIDstr(i).c_str(), WiFi.RSSI(i), 
            gps.location.lat(), gps.location.lng(), 
            gps.hdop.hdop(), gps.altitude.meters(), gps.speed.kmph());
        }
        logFile.close();
        // Indikácia zápisu (biely záblesk)
        setLED(255, 255, 255); delay(20); setLED(0, 255, 0);
      }
    }
    WiFi.scanDelete();
  }
}
