#include <WiFi.h>

const char *ssid = "ESP32_AP";
const char *password = "12345678";

WiFiServer server(5000);

void setup() {
  Serial.begin(115200);
  WiFi.softAP(ssid, password);  // Crea la red Wi-Fi
  Serial.print("IP del AP: ");
  Serial.println(WiFi.softAPIP());
  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    String data = client.readStringUntil('\n');
    Serial.print("Recibido: ");
    Serial.println(data);
  }
}
