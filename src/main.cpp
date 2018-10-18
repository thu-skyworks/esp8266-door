#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <sstream>
#include <string>
#include <vector>
#include <cstdint>

#define __DEBUG__

#include "secrets.h"

char buf[50];

WiFiClient espClient;
PubSubClient client(espClient);

String action, pubTopic, pubMsg;

const char *openDoor = "open";
const char *subTopic = "/command";

void door_open() {
  digitalWrite(0, HIGH);
  delay(500);
  digitalWrite(0, LOW);
}

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("[wifi] Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  randomSeed(micros());

#ifdef __DEBUG__
  Serial.println("");
  Serial.println("[wifi] WiFi connected");
  Serial.println("[wifi] IP address: ");
  Serial.println(WiFi.localIP());
#endif
}

void callback(char *topic, byte *payload, unsigned int length) {
  String recTopic = topic;
  String recMsg = (char *)payload;
  recMsg = recMsg.substring(0, length);

#ifdef __DEBUG__
  Serial.println("[mqtt] Received " + recMsg + " of length " + length +
                 " from topic " + recTopic);
#endif

  if ((strcmp(recMsg.c_str(), openDoor) == 0) &&
      (strcmp(topic, subTopic) == 0)) {
#ifdef __DEBUG__
    Serial.println("[mqtt] Door opening, welcome!");
#endif
    door_open();
  }
}

void reconnect() {
  while (!client.connected()) {
#ifdef __DEBUG__
    Serial.println("[mqtt] Connection lost, attempting to reconnect...");
#endif
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      client.subscribe(subTopic);
    } else {
      Serial.print("[mqtt] Error Connecting: ");
      Serial.println(client.state());
      delay(500);
    }
  }
}

void setup() {
  pinMode(0, OUTPUT);
  pinMode(2, OUTPUT);
  digitalWrite(2, LOW); // REn=0, Receiver Output Enable. 
  digitalWrite(0, HIGH);
  Serial.begin(9600);
  // Serial.setTimeout(300);

  setup_wifi();
  client.setServer(mqtt_broker, 1883);
  client.setCallback(callback);
}

void printSerial() {
    String msg = "[rs485] Recv: ";
    for (int i = 0; i < 30; i++) {
      msg += String(buf[i], HEX);
      msg += " ";
      // buf[i] = 0x00;
    }
    client.publish("/log", msg.c_str());
}

void loop() {
  unsigned long cardid;

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (Serial.available()) {
    // tmp = Serial.read();
    Serial.readBytes(buf, 50);
    printSerial();

    if (buf[0] == 0x02) {
      if ((buf[1] == 0x01) && (buf[2] == 0x0F)) {
        cardid = (buf[9] << 24) + (buf[10] << 16) + (buf[11] << 8) + buf[12];
        client.publish("/cardverify", String(cardid).c_str());
#ifdef __DEBUG__
        client.publish(
            "/log", ("[nfc] Card detected, cardid=" + String(cardid)).c_str());
#endif
      }
    }
    for(int i = 0; i < 50; i++) buf[i] = 0x00;
  }
}
