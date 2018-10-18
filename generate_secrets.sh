#!/bin/bash
cat >src/secrets.h <<<EOF
#pragma once

const char *ssid = "$PRJ_CFG_SSID";   // WiFi SSID
const char *password = "$PRJ_CFG_PSK"; // WiFi PSK

const char *mqtt_broker = "$PRJ_CFG_BROKER"; // MQTT Broker

const char *mqtt_user = "$PRJ_CFG_MQTT_USER";               // MQTT Username
const char *mqtt_password = "$PRJ_CFG_MQTT_PASSWD"; // MQTT Password
EOF