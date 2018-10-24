#!/bin/bash
cat >src/secrets.h <<EOF
#pragma once

const char *ssid = "$PRJ_CFG_SSID";   // WiFi SSID
const char *password = "$PRJ_CFG_PSK"; // WiFi PSK

const char *mqtt_broker = "$PRJ_CFG_BROKER"; // MQTT Broker

const char *mqtt_user = "$PRJ_CFG_MQTT_USER";               // MQTT Username
const char *mqtt_password = "$PRJ_CFG_MQTT_PASSWD"; // MQTT Password
EOF

cat >config.py <<EOF
MQTT_BROKER = "$PRJ_CFG_BROKER" # MQTT Broker
MQTT_USER = "$PRJ_CFG_MQTT_USER"               # MQTT Username
MQTT_PASSWORD = "$PRJ_CFG_MQTT_PASSWD" # MQTT Password

DBNAME = "$PRJ_CFG_DBNAME"
DBUSER = "$PRJ_CFG_DBUSER"
DBPASS = "$PRJ_CFG_DBPASS"

LDAP_URI  = "$PRJ_CFG_LDAP_URI"
LDAP_USER = "$PRJ_CFG_LDAP_USER"
LDAP_PASS = "$PRJ_CFG_LDAP_PASS"


EOF
