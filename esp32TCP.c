#include <WiFi.h>

const char* ssid = "TU_SSID";
const char* password = "TU_PASSWORD";

WiFiServer server(5000);  // Puerto TCP 5000

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado a WiFi");
  Serial.print("IP ESP32: ");
  Serial.println(WiFi.localIP());

  server.begin(); // Inicia el servidor
}

void loop() {
  WiFiClient client = server.available(); // Espera cliente
  if (client) {
    Serial.println("Cliente conectado");
    while (client.connected()) {
      if (client.available()) {
        String data = client.readStringUntil('\n'); // Lee string hasta salto de línea
        Serial.print("Recibido: ");
        Serial.println(data);
        // Aquí podrías imprimirlo en tu pantalla LCD
      }
    }
    client.stop();
    Serial.println("Cliente desconectado");
  }
}
