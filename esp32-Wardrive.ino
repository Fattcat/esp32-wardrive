#include <WiFi.h>
#include <TinyGPS++.h>
#include <FS.h>
#include <SD.h>

TinyGPSPlus gps;
File logFile;

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, 16, 17); // GPS na piny 16, 17
  SD.begin(5);
  
  // Hlavička CSV
  logFile = SD.open("/wardrive.csv", FILE_APPEND);
  if (logFile) {
    logFile.println("bssid,rssi,lat,lon,hdop,alt");
    logFile.close();
  }
}

void loop() {
  while (Serial2.available() > 0) {
    gps.encode(Serial2.read());
  }

  // Skenujeme len ak máme GPS fix a rozumnú presnosť
  if (gps.location.isValid() && gps.hdop.hdop() < 2.5) {
    int n = WiFi.scanNetworks(true, false, false, 100); 
    
    logFile = SD.open("/wardrive.csv", FILE_APPEND);
    for (int i = 0; i < n; ++i) {
      logFile.printf("%s,%d,%.6f,%.6f,%.2f,%.1f\n", 
        WiFi.BSSIDstr(i).c_str(), 
        WiFi.RSSI(i), 
        gps.location.lat(), 
        gps.location.lng(), 
        gps.hdop.hdop(),
        gps.altitude.meters());
    }
    logFile.close();
    WiFi.scanDelete();
  }
}
