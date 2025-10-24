# Expo-Aprigio
Projeto da Expo Aprígio envolvendo leitura e exibição de tensão gerada a partir de energia solar

Código do Esp32 atualizado para enviar os dados a interface:
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define SENSOR_PIN 34

const char* ssid = "SEU_WIFI";
const char* password = "SENHA_WIFI";
const char* serverUrl = "https://seu-site.com/dado";  // Backend que irá receber a tensão

const float VREF = 3.3;
const int ADC_RES = 4095;
const float DIVISOR = 11.0;

bool piscar = false;
unsigned long ultimoTempo = 0;
const unsigned long intervaloPiscar = 600;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Conectando ao WiFi...");
  }
  Serial.println("WiFi conectado!");

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
}

void loop() {
  int valorADC = analogRead(SENSOR_PIN);
  float tensao = (valorADC * VREF / ADC_RES) * DIVISOR;

  enviarParaServidor(tensao);

  if (millis() - ultimoTempo > intervaloPiscar) {
    piscar = !piscar;
    ultimoTempo = millis();
  }

  desenharTela(tensao, piscar);
  delay(2000); // envia a cada 2 segundos
}

void enviarParaServidor(float tensao) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String json = "{\"tensao\":" + String(tensao, 2) + "}";
    http.POST(json);
    http.end();
  }
}